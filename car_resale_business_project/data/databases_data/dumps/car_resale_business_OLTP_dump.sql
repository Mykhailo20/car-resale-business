--
-- PostgreSQL database dump
--

-- Dumped from database version 15.2
-- Dumped by pg_dump version 15.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: car_condition_domain; Type: DOMAIN; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE DOMAIN public.car_condition_domain AS numeric(2,1)
	CONSTRAINT car_condition_domain_check CHECK (((VALUE >= 1.0) AND (VALUE <= 5.0)));


ALTER DOMAIN public.car_condition_domain OWNER TO mykhailo_lozinskyi;

--
-- Name: email_domain; Type: DOMAIN; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE DOMAIN public.email_domain AS character varying(100)
	CONSTRAINT email_domain_check CHECK (((VALUE)::text ~ '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+.[A-Za-z]{2,4}$'::text));


ALTER DOMAIN public.email_domain OWNER TO mykhailo_lozinskyi;

--
-- Name: non_negative_domain; Type: DOMAIN; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE DOMAIN public.non_negative_domain AS integer
	CONSTRAINT non_negative_domain_check CHECK ((VALUE >= 0));


ALTER DOMAIN public.non_negative_domain OWNER TO mykhailo_lozinskyi;

--
-- Name: person_name_domain; Type: DOMAIN; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE DOMAIN public.person_name_domain AS character varying(50)
	CONSTRAINT person_name_domain_check CHECK (((VALUE)::text ~ '^[A-Za-z]+$'::text));


ALTER DOMAIN public.person_name_domain OWNER TO mykhailo_lozinskyi;

--
-- Name: repair_type_enum; Type: TYPE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TYPE public.repair_type_enum AS ENUM (
    'painting',
    'mechanical_repair',
    'body_repair',
    'electrical_repair'
);


ALTER TYPE public.repair_type_enum OWNER TO mykhailo_lozinskyi;

--
-- Name: seller_type_enum; Type: TYPE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TYPE public.seller_type_enum AS ENUM (
    'car_manufacturing_company',
    'financial_institution',
    'car_rental_company',
    'dealership',
    'individual'
);


ALTER TYPE public.seller_type_enum OWNER TO mykhailo_lozinskyi;

--
-- Name: sex_enum; Type: TYPE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TYPE public.sex_enum AS ENUM (
    'female',
    'male'
);


ALTER TYPE public.sex_enum OWNER TO mykhailo_lozinskyi;

--
-- Name: transmission_enum; Type: TYPE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TYPE public.transmission_enum AS ENUM (
    'automatic',
    'manual'
);


ALTER TYPE public.transmission_enum OWNER TO mykhailo_lozinskyi;

--
-- Name: url_domain; Type: DOMAIN; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE DOMAIN public.url_domain AS character varying(2048)
	CONSTRAINT url_domain_check CHECK (((VALUE)::text ~ '^https?://[^\s/$.?#].[^\s]*$'::text));


ALTER DOMAIN public.url_domain OWNER TO mykhailo_lozinskyi;

--
-- Name: check_estimation_date_trigger_function(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.check_estimation_date_trigger_function() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    purchase_date_local DATE;
    purchase_price_local NUMERIC;
    repair_costs_total_local NUMERIC;
BEGIN
    -- Check if estimation_date is in the future
    IF NEW.estimation_date > CURRENT_DATE THEN
        RAISE EXCEPTION 'Estimation date cannot be in the future.';
    END IF;

    -- Check if the car has been purchased
    SELECT purchase_date, price INTO purchase_date_local, purchase_price_local
    FROM purchase
    WHERE car_vin = NEW.car_vin;

    IF purchase_date_local IS NULL THEN
        RAISE EXCEPTION 'Car has not been purchased, cannot create an estimation entry.';
    END IF;

    -- Check if estimation_date is after the purchase_date
    IF NEW.estimation_date < purchase_date_local THEN
        RAISE EXCEPTION 'Estimation date must be after the purchase date of the specified car.';
    END IF;

    -- Check if the car has already been sold
    IF EXISTS (
        SELECT 1
        FROM sale
        WHERE car_vin = NEW.car_vin
    ) THEN
        RAISE EXCEPTION 'Car has already been sold, cannot create an estimation entry.';
    END IF;

    -- Check if estimation.price is greater than purchase.price
    IF NEW.price < purchase_price_local THEN
        RAISE EXCEPTION 'Estimation price must be greater than or equal to the purchase price.';
    END IF;

    -- Check if there are records for the specified car_vin in the repair table
    SELECT COALESCE(SUM(cost), 0) INTO repair_costs_total_local
    FROM repair
    WHERE car_vin = NEW.car_vin;

    IF NEW.price < (purchase_price_local + repair_costs_total_local) THEN
        RAISE EXCEPTION 'The estimated price must be greater than or equal to the sum of the purchase price and the repair costs.';
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_estimation_date_trigger_function() OWNER TO postgres;

--
-- Name: check_purchase_date_trigger_function(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.check_purchase_date_trigger_function() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Check if purchase_date is in the future
    IF NEW.purchase_date > CURRENT_DATE THEN
        RAISE EXCEPTION 'Purchase date cannot be in the future.';
    END IF;

    -- Check if purchase_date is after 1990
    IF NEW.purchase_date < DATE '1990-01-01' THEN
        RAISE EXCEPTION 'Purchase date must be after 1990.';
    END IF;

    -- Check if purchase_date.year >= car.manufacture_year
    IF EXTRACT(YEAR FROM NEW.purchase_date) < (SELECT manufacture_year FROM car WHERE vin = NEW.car_vin) THEN
        RAISE EXCEPTION 'Purchase date must be after or equal to car manufacture year.';
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_purchase_date_trigger_function() OWNER TO postgres;

--
-- Name: check_repair_date_trigger_function(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.check_repair_date_trigger_function() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    purchase_date_local DATE;
BEGIN
    -- Check if repair_date is in the future
    IF NEW.repair_date > CURRENT_DATE THEN
        RAISE EXCEPTION 'Repair date cannot be in the future.';
    END IF;

    -- Check if the car has been purchased
    SELECT purchase_date INTO purchase_date_local
    FROM purchase
    WHERE car_vin = NEW.car_vin;

    IF purchase_date_local IS NULL THEN
        RAISE EXCEPTION 'Car has not been purchased, cannot create a repair entry.';
    END IF;

    -- Check if repair_date is after the purchase_date
    IF NEW.repair_date < purchase_date_local THEN
        RAISE EXCEPTION 'Repair date must be after the purchase date of the specified car.';
    END IF;

    -- Check if the car has already been sold
    IF EXISTS (
        SELECT 1
        FROM sale
        WHERE car_vin = NEW.car_vin
    ) THEN
        RAISE EXCEPTION 'Car has already been sold, cannot create a repair entry.';
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_repair_date_trigger_function() OWNER TO postgres;

--
-- Name: check_sale_date_trigger_function(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.check_sale_date_trigger_function() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    purchase_date_local DATE;
    last_repair_date_local DATE;
	last_estimation_date_local DATE;
BEGIN
    -- Check if sale_date is in the future
    IF NEW.sale_date > CURRENT_DATE THEN
        RAISE EXCEPTION 'Sale date cannot be in the future.';
    END IF;

    -- Check if the car has been purchased
    SELECT purchase_date INTO purchase_date_local
    FROM purchase
    WHERE car_vin = NEW.car_vin;

    IF purchase_date_local IS NULL THEN
        RAISE EXCEPTION 'Car has not been purchased, cannot create a sale entry.';
    END IF;

    -- Check if sale_date is after the purchase_date
    IF NEW.sale_date < purchase_date_local THEN
        RAISE EXCEPTION 'Sale date must be after the purchase date of the specified car.';
    END IF;

    -- Check if additional repairs have been performed on the car
    SELECT MAX(repair_date) INTO last_repair_date_local
    FROM repair
    WHERE car_vin = NEW.car_vin;

    IF last_repair_date_local IS NOT NULL AND NEW.sale_date < last_repair_date_local THEN
        RAISE EXCEPTION 'Sale date must be after the last repair date of the specified car.';
    END IF;
	
	-- Check if the car has been estimated
    SELECT MAX(estimation_date) INTO last_estimation_date_local
    FROM estimation
    WHERE car_vin = NEW.car_vin;

    IF last_estimation_date_local IS NOT NULL AND NEW.sale_date < last_estimation_date_local THEN
        RAISE EXCEPTION 'Sale date must be after the last estimation date of the specified car.';
    END IF;
	
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_sale_date_trigger_function() OWNER TO postgres;

--
-- Name: update_updated_at_trigger_function(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_trigger_function() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_trigger_function() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: address; Type: TABLE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TABLE public.address (
    address_id integer NOT NULL,
    city_id integer,
    street character varying(100),
    postal_code character varying(15),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.address OWNER TO mykhailo_lozinskyi;

--
-- Name: address_address_id_seq; Type: SEQUENCE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE SEQUENCE public.address_address_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.address_address_id_seq OWNER TO mykhailo_lozinskyi;

--
-- Name: address_address_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER SEQUENCE public.address_address_id_seq OWNED BY public.address.address_id;


--
-- Name: person; Type: TABLE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TABLE public.person (
    person_id integer NOT NULL,
    first_name public.person_name_domain NOT NULL,
    last_name public.person_name_domain NOT NULL,
    middle_name public.person_name_domain,
    birth_date date,
    sex public.sex_enum,
    email public.email_domain,
    CONSTRAINT person_birth_date_check CHECK (((birth_date >= (CURRENT_DATE - '100 years'::interval)) AND (birth_date <= (CURRENT_DATE - '16 years'::interval))))
);


ALTER TABLE public.person OWNER TO mykhailo_lozinskyi;

--
-- Name: buyer; Type: TABLE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TABLE public.buyer (
    address_id integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
)
INHERITS (public.person);


ALTER TABLE public.buyer OWNER TO mykhailo_lozinskyi;

--
-- Name: car; Type: TABLE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TABLE public.car (
    vin character varying(17) NOT NULL,
    manufacture_year smallint NOT NULL,
    make_id integer,
    model character varying(50) NOT NULL,
    "trim" character varying(100),
    body_type_id integer,
    transmission public.transmission_enum NOT NULL,
    color_id integer,
    description text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT car_manufacture_year_check CHECK ((manufacture_year >= 1900)),
    CONSTRAINT vin_charset_check CHECK (((vin)::text ~ '^[A-Z0-9]+$'::text))
);


ALTER TABLE public.car OWNER TO mykhailo_lozinskyi;

--
-- Name: car_body_type; Type: TABLE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TABLE public.car_body_type (
    car_body_type_id integer NOT NULL,
    name character varying(50),
    description text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT car_body_type_name_check CHECK (((name)::text ~ '^[A-Za-z0-9 -]+$'::text))
);


ALTER TABLE public.car_body_type OWNER TO mykhailo_lozinskyi;

--
-- Name: car_body_type_car_body_type_id_seq; Type: SEQUENCE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE SEQUENCE public.car_body_type_car_body_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.car_body_type_car_body_type_id_seq OWNER TO mykhailo_lozinskyi;

--
-- Name: car_body_type_car_body_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER SEQUENCE public.car_body_type_car_body_type_id_seq OWNED BY public.car_body_type.car_body_type_id;


--
-- Name: car_make; Type: TABLE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TABLE public.car_make (
    car_make_id integer NOT NULL,
    name character varying(255) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.car_make OWNER TO mykhailo_lozinskyi;

--
-- Name: car_make_care_make_id_seq; Type: SEQUENCE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE SEQUENCE public.car_make_care_make_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.car_make_care_make_id_seq OWNER TO mykhailo_lozinskyi;

--
-- Name: car_make_care_make_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER SEQUENCE public.car_make_care_make_id_seq OWNED BY public.car_make.car_make_id;


--
-- Name: city; Type: TABLE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TABLE public.city (
    city_id integer NOT NULL,
    country_id integer,
    name character varying(100) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT name_constraint CHECK (((name)::text ~ '^[A-Za-z ]+$'::text))
);


ALTER TABLE public.city OWNER TO mykhailo_lozinskyi;

--
-- Name: city_city_id_seq; Type: SEQUENCE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE SEQUENCE public.city_city_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.city_city_id_seq OWNER TO mykhailo_lozinskyi;

--
-- Name: city_city_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER SEQUENCE public.city_city_id_seq OWNED BY public.city.city_id;


--
-- Name: color; Type: TABLE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TABLE public.color (
    color_id integer NOT NULL,
    name character varying(50) NOT NULL,
    hex_code character varying(6),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT color_hex_code_check CHECK (((hex_code)::text ~ '^[0-9A-Fa-f]{6}$'::text)),
    CONSTRAINT color_name_check CHECK (((name)::text ~ '^[a-zA-Z-]+$'::text))
);


ALTER TABLE public.color OWNER TO mykhailo_lozinskyi;

--
-- Name: color_color_id_seq; Type: SEQUENCE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE SEQUENCE public.color_color_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.color_color_id_seq OWNER TO mykhailo_lozinskyi;

--
-- Name: color_color_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER SEQUENCE public.color_color_id_seq OWNED BY public.color.color_id;


--
-- Name: country; Type: TABLE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TABLE public.country (
    country_id integer NOT NULL,
    name character varying(64) NOT NULL,
    iso character varying(2) NOT NULL,
    iso3 character varying(3),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT country_iso3_check CHECK (((iso3)::text ~ '^[A-Z]{3}$'::text)),
    CONSTRAINT country_iso_check CHECK (((iso)::text ~ '^[A-Z]{2}$'::text)),
    CONSTRAINT country_name_check CHECK (((name)::text ~ '^[A-Za-z ]+$'::text))
);


ALTER TABLE public.country OWNER TO mykhailo_lozinskyi;

--
-- Name: country_country_id_seq; Type: SEQUENCE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE SEQUENCE public.country_country_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.country_country_id_seq OWNER TO mykhailo_lozinskyi;

--
-- Name: country_country_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER SEQUENCE public.country_country_id_seq OWNED BY public.country.country_id;


--
-- Name: employee; Type: TABLE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TABLE public.employee (
    position_id integer,
    salary public.non_negative_domain NOT NULL,
    hire_date date NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT employee_hire_date_check CHECK (((hire_date >= (CURRENT_DATE - '100 years'::interval)) AND (hire_date <= (CURRENT_DATE - '1 mon'::interval))))
)
INHERITS (public.person);


ALTER TABLE public.employee OWNER TO mykhailo_lozinskyi;

--
-- Name: estimation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estimation (
    estimation_id integer NOT NULL,
    car_vin character varying(17),
    price public.non_negative_domain NOT NULL,
    estimation_date date NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.estimation OWNER TO postgres;

--
-- Name: estimation_estimation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.estimation_estimation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.estimation_estimation_id_seq OWNER TO postgres;

--
-- Name: estimation_estimation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.estimation_estimation_id_seq OWNED BY public.estimation.estimation_id;


--
-- Name: person_person_id_seq; Type: SEQUENCE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE SEQUENCE public.person_person_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.person_person_id_seq OWNER TO mykhailo_lozinskyi;

--
-- Name: person_person_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER SEQUENCE public.person_person_id_seq OWNED BY public.person.person_id;


--
-- Name: position; Type: TABLE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TABLE public."position" (
    position_id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public."position" OWNER TO mykhailo_lozinskyi;

--
-- Name: position_position_id_seq; Type: SEQUENCE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE SEQUENCE public.position_position_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.position_position_id_seq OWNER TO mykhailo_lozinskyi;

--
-- Name: position_position_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER SEQUENCE public.position_position_id_seq OWNED BY public."position".position_id;


--
-- Name: purchase; Type: TABLE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TABLE public.purchase (
    car_vin character varying(17) NOT NULL,
    seller_id integer NOT NULL,
    employee_id integer NOT NULL,
    price public.non_negative_domain,
    odometer public.non_negative_domain,
    condition public.car_condition_domain,
    description text,
    car_image bytea,
    purchase_date date,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    car_image_content_type character varying(10)
);


ALTER TABLE public.purchase OWNER TO mykhailo_lozinskyi;

--
-- Name: repair; Type: TABLE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TABLE public.repair (
    repair_id integer NOT NULL,
    car_vin character varying(17) NOT NULL,
    employee_id integer NOT NULL,
    address_id integer,
    repair_type public.repair_type_enum,
    cost public.non_negative_domain,
    condition public.car_condition_domain,
    description text,
    repair_date date,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.repair OWNER TO mykhailo_lozinskyi;

--
-- Name: repair_repair_id_seq; Type: SEQUENCE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE SEQUENCE public.repair_repair_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repair_repair_id_seq OWNER TO mykhailo_lozinskyi;

--
-- Name: repair_repair_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER SEQUENCE public.repair_repair_id_seq OWNED BY public.repair.repair_id;


--
-- Name: sale; Type: TABLE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TABLE public.sale (
    car_vin character varying(17) NOT NULL,
    buyer_id integer NOT NULL,
    employee_id integer NOT NULL,
    mmr public.non_negative_domain,
    price public.non_negative_domain,
    odometer public.non_negative_domain,
    condition public.car_condition_domain,
    car_image bytea,
    description text,
    sale_date date,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    car_image_content_type character varying(10)
);


ALTER TABLE public.sale OWNER TO mykhailo_lozinskyi;

--
-- Name: seller; Type: TABLE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TABLE public.seller (
    seller_id integer NOT NULL,
    name character varying(100) NOT NULL,
    type public.seller_type_enum,
    address_id integer,
    email public.email_domain,
    website_url public.url_domain,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.seller OWNER TO mykhailo_lozinskyi;

--
-- Name: seller_seller_id_seq; Type: SEQUENCE; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE SEQUENCE public.seller_seller_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seller_seller_id_seq OWNER TO mykhailo_lozinskyi;

--
-- Name: seller_seller_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER SEQUENCE public.seller_seller_id_seq OWNED BY public.seller.seller_id;


--
-- Name: address address_id; Type: DEFAULT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.address ALTER COLUMN address_id SET DEFAULT nextval('public.address_address_id_seq'::regclass);


--
-- Name: buyer person_id; Type: DEFAULT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.buyer ALTER COLUMN person_id SET DEFAULT nextval('public.person_person_id_seq'::regclass);


--
-- Name: car_body_type car_body_type_id; Type: DEFAULT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.car_body_type ALTER COLUMN car_body_type_id SET DEFAULT nextval('public.car_body_type_car_body_type_id_seq'::regclass);


--
-- Name: car_make car_make_id; Type: DEFAULT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.car_make ALTER COLUMN car_make_id SET DEFAULT nextval('public.car_make_care_make_id_seq'::regclass);


--
-- Name: city city_id; Type: DEFAULT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.city ALTER COLUMN city_id SET DEFAULT nextval('public.city_city_id_seq'::regclass);


--
-- Name: color color_id; Type: DEFAULT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.color ALTER COLUMN color_id SET DEFAULT nextval('public.color_color_id_seq'::regclass);


--
-- Name: country country_id; Type: DEFAULT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.country ALTER COLUMN country_id SET DEFAULT nextval('public.country_country_id_seq'::regclass);


--
-- Name: employee person_id; Type: DEFAULT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.employee ALTER COLUMN person_id SET DEFAULT nextval('public.person_person_id_seq'::regclass);


--
-- Name: estimation estimation_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estimation ALTER COLUMN estimation_id SET DEFAULT nextval('public.estimation_estimation_id_seq'::regclass);


--
-- Name: person person_id; Type: DEFAULT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.person ALTER COLUMN person_id SET DEFAULT nextval('public.person_person_id_seq'::regclass);


--
-- Name: position position_id; Type: DEFAULT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public."position" ALTER COLUMN position_id SET DEFAULT nextval('public.position_position_id_seq'::regclass);


--
-- Name: repair repair_id; Type: DEFAULT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.repair ALTER COLUMN repair_id SET DEFAULT nextval('public.repair_repair_id_seq'::regclass);


--
-- Name: seller seller_id; Type: DEFAULT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.seller ALTER COLUMN seller_id SET DEFAULT nextval('public.seller_seller_id_seq'::regclass);


--
-- Data for Name: address; Type: TABLE DATA; Schema: public; Owner: mykhailo_lozinskyi
--

COPY public.address (address_id, city_id, street, postal_code, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: buyer; Type: TABLE DATA; Schema: public; Owner: mykhailo_lozinskyi
--

COPY public.buyer (person_id, first_name, last_name, middle_name, birth_date, sex, email, address_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: car; Type: TABLE DATA; Schema: public; Owner: mykhailo_lozinskyi
--

COPY public.car (vin, manufacture_year, make_id, model, "trim", body_type_id, transmission, color_id, description, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: car_body_type; Type: TABLE DATA; Schema: public; Owner: mykhailo_lozinskyi
--

COPY public.car_body_type (car_body_type_id, name, description, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: car_make; Type: TABLE DATA; Schema: public; Owner: mykhailo_lozinskyi
--

COPY public.car_make (car_make_id, name, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: city; Type: TABLE DATA; Schema: public; Owner: mykhailo_lozinskyi
--

COPY public.city (city_id, country_id, name, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: color; Type: TABLE DATA; Schema: public; Owner: mykhailo_lozinskyi
--

COPY public.color (color_id, name, hex_code, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: country; Type: TABLE DATA; Schema: public; Owner: mykhailo_lozinskyi
--

COPY public.country (country_id, name, iso, iso3, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: employee; Type: TABLE DATA; Schema: public; Owner: mykhailo_lozinskyi
--

COPY public.employee (person_id, first_name, last_name, middle_name, birth_date, sex, email, position_id, salary, hire_date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: estimation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.estimation (estimation_id, car_vin, price, estimation_date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: person; Type: TABLE DATA; Schema: public; Owner: mykhailo_lozinskyi
--

COPY public.person (person_id, first_name, last_name, middle_name, birth_date, sex, email) FROM stdin;
\.


--
-- Data for Name: position; Type: TABLE DATA; Schema: public; Owner: mykhailo_lozinskyi
--

COPY public."position" (position_id, name, description, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: purchase; Type: TABLE DATA; Schema: public; Owner: mykhailo_lozinskyi
--

COPY public.purchase (car_vin, seller_id, employee_id, price, odometer, condition, description, car_image, purchase_date, created_at, updated_at, car_image_content_type) FROM stdin;
\.


--
-- Data for Name: repair; Type: TABLE DATA; Schema: public; Owner: mykhailo_lozinskyi
--

COPY public.repair (repair_id, car_vin, employee_id, address_id, repair_type, cost, condition, description, repair_date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sale; Type: TABLE DATA; Schema: public; Owner: mykhailo_lozinskyi
--

COPY public.sale (car_vin, buyer_id, employee_id, mmr, price, odometer, condition, car_image, description, sale_date, created_at, updated_at, car_image_content_type) FROM stdin;
\.


--
-- Data for Name: seller; Type: TABLE DATA; Schema: public; Owner: mykhailo_lozinskyi
--

COPY public.seller (seller_id, name, type, address_id, email, website_url, created_at, updated_at) FROM stdin;
\.


--
-- Name: address_address_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mykhailo_lozinskyi
--

SELECT pg_catalog.setval('public.address_address_id_seq', 29790, true);


--
-- Name: car_body_type_car_body_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mykhailo_lozinskyi
--

SELECT pg_catalog.setval('public.car_body_type_car_body_type_id_seq', 77, true);


--
-- Name: car_make_care_make_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mykhailo_lozinskyi
--

SELECT pg_catalog.setval('public.car_make_care_make_id_seq', 54, true);


--
-- Name: city_city_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mykhailo_lozinskyi
--

SELECT pg_catalog.setval('public.city_city_id_seq', 35, true);


--
-- Name: color_color_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mykhailo_lozinskyi
--

SELECT pg_catalog.setval('public.color_color_id_seq', 21, true);


--
-- Name: country_country_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mykhailo_lozinskyi
--

SELECT pg_catalog.setval('public.country_country_id_seq', 6, true);


--
-- Name: estimation_estimation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.estimation_estimation_id_seq', 1, false);


--
-- Name: person_person_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mykhailo_lozinskyi
--

SELECT pg_catalog.setval('public.person_person_id_seq', 237, true);


--
-- Name: position_position_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mykhailo_lozinskyi
--

SELECT pg_catalog.setval('public.position_position_id_seq', 5, true);


--
-- Name: repair_repair_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mykhailo_lozinskyi
--

SELECT pg_catalog.setval('public.repair_repair_id_seq', 20, true);


--
-- Name: seller_seller_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mykhailo_lozinskyi
--

SELECT pg_catalog.setval('public.seller_seller_id_seq', 29697, true);


--
-- Name: address address_pkey; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.address
    ADD CONSTRAINT address_pkey PRIMARY KEY (address_id);


--
-- Name: car_body_type car_body_type_name_key; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.car_body_type
    ADD CONSTRAINT car_body_type_name_key UNIQUE (name);


--
-- Name: car_body_type car_body_type_pkey; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.car_body_type
    ADD CONSTRAINT car_body_type_pkey PRIMARY KEY (car_body_type_id);


--
-- Name: car_make car_make_name_key; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.car_make
    ADD CONSTRAINT car_make_name_key UNIQUE (name);


--
-- Name: car_make car_make_pkey; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.car_make
    ADD CONSTRAINT car_make_pkey PRIMARY KEY (car_make_id);


--
-- Name: car car_pkey; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.car
    ADD CONSTRAINT car_pkey PRIMARY KEY (vin);


--
-- Name: city city_pkey; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.city
    ADD CONSTRAINT city_pkey PRIMARY KEY (city_id);


--
-- Name: color color_name_key; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.color
    ADD CONSTRAINT color_name_key UNIQUE (name);


--
-- Name: color color_pkey; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.color
    ADD CONSTRAINT color_pkey PRIMARY KEY (color_id);


--
-- Name: country country_pkey; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.country
    ADD CONSTRAINT country_pkey PRIMARY KEY (country_id);


--
-- Name: estimation estimation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estimation
    ADD CONSTRAINT estimation_pkey PRIMARY KEY (estimation_id);


--
-- Name: person person_pkey; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.person
    ADD CONSTRAINT person_pkey PRIMARY KEY (person_id);


--
-- Name: position position_pkey; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public."position"
    ADD CONSTRAINT position_pkey PRIMARY KEY (position_id);


--
-- Name: purchase purchase_pkey; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.purchase
    ADD CONSTRAINT purchase_pkey PRIMARY KEY (car_vin);


--
-- Name: repair repair_pkey; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.repair
    ADD CONSTRAINT repair_pkey PRIMARY KEY (repair_id);


--
-- Name: sale sale_pkey; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.sale
    ADD CONSTRAINT sale_pkey PRIMARY KEY (car_vin);


--
-- Name: seller seller_pkey; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.seller
    ADD CONSTRAINT seller_pkey PRIMARY KEY (seller_id);


--
-- Name: buyer unique_buyer_person_id; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.buyer
    ADD CONSTRAINT unique_buyer_person_id UNIQUE (person_id);


--
-- Name: country unique_country_iso3_constraint; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.country
    ADD CONSTRAINT unique_country_iso3_constraint UNIQUE (iso3);


--
-- Name: country unique_country_iso_constraint; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.country
    ADD CONSTRAINT unique_country_iso_constraint UNIQUE (iso);


--
-- Name: employee unique_employee_person_id; Type: CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT unique_employee_person_id UNIQUE (person_id);


--
-- Name: car_make_id_model_index; Type: INDEX; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE INDEX car_make_id_model_index ON public.car USING btree (make_id, model);


--
-- Name: car_make_name_index; Type: INDEX; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE INDEX car_make_name_index ON public.car_make USING btree (name);


--
-- Name: address address_update_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER address_update_trigger BEFORE UPDATE ON public.address FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();


--
-- Name: buyer buyer_update_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER buyer_update_trigger BEFORE UPDATE ON public.buyer FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();


--
-- Name: car_body_type car_body_type_update_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER car_body_type_update_trigger BEFORE UPDATE ON public.car_body_type FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();


--
-- Name: car_make car_make_update_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER car_make_update_trigger BEFORE UPDATE ON public.car_make FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();


--
-- Name: car car_update_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER car_update_trigger BEFORE UPDATE ON public.car FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();


--
-- Name: estimation check_estimation_date_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER check_estimation_date_trigger BEFORE INSERT OR UPDATE ON public.estimation FOR EACH ROW EXECUTE FUNCTION public.check_estimation_date_trigger_function();


--
-- Name: purchase check_purchase_date_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER check_purchase_date_trigger BEFORE INSERT OR UPDATE ON public.purchase FOR EACH ROW EXECUTE FUNCTION public.check_purchase_date_trigger_function();


--
-- Name: repair check_repair_date_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER check_repair_date_trigger BEFORE INSERT OR UPDATE ON public.repair FOR EACH ROW EXECUTE FUNCTION public.check_repair_date_trigger_function();


--
-- Name: sale check_sale_date_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER check_sale_date_trigger BEFORE INSERT OR UPDATE ON public.sale FOR EACH ROW EXECUTE FUNCTION public.check_sale_date_trigger_function();


--
-- Name: city city_update_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER city_update_trigger BEFORE UPDATE ON public.city FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();


--
-- Name: color color_update_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER color_update_trigger BEFORE UPDATE ON public.color FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();


--
-- Name: country country_update_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER country_update_trigger BEFORE UPDATE ON public.country FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();


--
-- Name: employee employee_update_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER employee_update_trigger BEFORE UPDATE ON public.employee FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();


--
-- Name: estimation estimation_update_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER estimation_update_trigger BEFORE UPDATE ON public.estimation FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();


--
-- Name: purchase purchase_update_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER purchase_update_trigger BEFORE UPDATE ON public.purchase FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();


--
-- Name: repair repair_update_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER repair_update_trigger BEFORE UPDATE ON public.repair FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();


--
-- Name: sale sale_update_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER sale_update_trigger BEFORE UPDATE ON public.sale FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();


--
-- Name: seller seller_update_trigger; Type: TRIGGER; Schema: public; Owner: mykhailo_lozinskyi
--

CREATE TRIGGER seller_update_trigger BEFORE UPDATE ON public.seller FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();


--
-- Name: address address_city_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.address
    ADD CONSTRAINT address_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.city(city_id);


--
-- Name: buyer buyer_address_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.buyer
    ADD CONSTRAINT buyer_address_id_fkey FOREIGN KEY (address_id) REFERENCES public.address(address_id);


--
-- Name: car car_body_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.car
    ADD CONSTRAINT car_body_type_id_fkey FOREIGN KEY (body_type_id) REFERENCES public.car_body_type(car_body_type_id);


--
-- Name: car car_color_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.car
    ADD CONSTRAINT car_color_id_fkey FOREIGN KEY (color_id) REFERENCES public.color(color_id);


--
-- Name: car car_make_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.car
    ADD CONSTRAINT car_make_id_fkey FOREIGN KEY (make_id) REFERENCES public.car_make(car_make_id);


--
-- Name: city city_country_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.city
    ADD CONSTRAINT city_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.country(country_id);


--
-- Name: employee employee_position_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_position_id_fkey FOREIGN KEY (position_id) REFERENCES public."position"(position_id);


--
-- Name: estimation estimation_car_vin_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estimation
    ADD CONSTRAINT estimation_car_vin_fkey FOREIGN KEY (car_vin) REFERENCES public.car(vin);


--
-- Name: purchase purchase_car_vin_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.purchase
    ADD CONSTRAINT purchase_car_vin_fkey FOREIGN KEY (car_vin) REFERENCES public.car(vin);


--
-- Name: purchase purchase_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.purchase
    ADD CONSTRAINT purchase_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(person_id);


--
-- Name: purchase purchase_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.purchase
    ADD CONSTRAINT purchase_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.seller(seller_id);


--
-- Name: repair repair_address_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.repair
    ADD CONSTRAINT repair_address_id_fkey FOREIGN KEY (address_id) REFERENCES public.address(address_id);


--
-- Name: repair repair_car_vin_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.repair
    ADD CONSTRAINT repair_car_vin_fkey FOREIGN KEY (car_vin) REFERENCES public.car(vin);


--
-- Name: repair repair_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.repair
    ADD CONSTRAINT repair_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(person_id);


--
-- Name: sale sale_buyer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.sale
    ADD CONSTRAINT sale_buyer_id_fkey FOREIGN KEY (buyer_id) REFERENCES public.buyer(person_id);


--
-- Name: sale sale_car_vin_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.sale
    ADD CONSTRAINT sale_car_vin_fkey FOREIGN KEY (car_vin) REFERENCES public.car(vin);


--
-- Name: sale sale_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.sale
    ADD CONSTRAINT sale_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(person_id);


--
-- Name: seller seller_address_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mykhailo_lozinskyi
--

ALTER TABLE ONLY public.seller
    ADD CONSTRAINT seller_address_id_fkey FOREIGN KEY (address_id) REFERENCES public.address(address_id);


--
-- PostgreSQL database dump complete
--

