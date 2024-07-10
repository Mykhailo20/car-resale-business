PGDMP     (                    |           car_resale_business_OLTP    15.2    15.2 �    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    85886    car_resale_business_OLTP    DATABASE     �   CREATE DATABASE "car_resale_business_OLTP" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Ukrainian_Ukraine.1251';
 *   DROP DATABASE "car_resale_business_OLTP";
                mykhailo_lozinskyi    false            d           1247    85888    car_condition_domain    DOMAIN     �   CREATE DOMAIN public.car_condition_domain AS numeric(2,1)
	CONSTRAINT car_condition_domain_check CHECK (((VALUE >= 1.0) AND (VALUE <= 5.0)));
 )   DROP DOMAIN public.car_condition_domain;
       public          mykhailo_lozinskyi    false            h           1247    85891    email_domain    DOMAIN     �   CREATE DOMAIN public.email_domain AS character varying(100)
	CONSTRAINT email_domain_check CHECK (((VALUE)::text ~ '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+.[A-Za-z]{2,4}$'::text));
 !   DROP DOMAIN public.email_domain;
       public          mykhailo_lozinskyi    false            l           1247    85894    non_negative_domain    DOMAIN     p   CREATE DOMAIN public.non_negative_domain AS integer
	CONSTRAINT non_negative_domain_check CHECK ((VALUE >= 0));
 (   DROP DOMAIN public.non_negative_domain;
       public          mykhailo_lozinskyi    false            p           1247    85897    person_name_domain    DOMAIN     �   CREATE DOMAIN public.person_name_domain AS character varying(50)
	CONSTRAINT person_name_domain_check CHECK (((VALUE)::text ~ '^[A-Za-z]+$'::text));
 '   DROP DOMAIN public.person_name_domain;
       public          mykhailo_lozinskyi    false            t           1247    85900    repair_type_enum    TYPE     �   CREATE TYPE public.repair_type_enum AS ENUM (
    'painting',
    'mechanical_repair',
    'body_repair',
    'electrical_repair'
);
 #   DROP TYPE public.repair_type_enum;
       public          mykhailo_lozinskyi    false            w           1247    85910    seller_type_enum    TYPE     �   CREATE TYPE public.seller_type_enum AS ENUM (
    'car_manufacturing_company',
    'financial_institution',
    'car_rental_company',
    'dealership',
    'individual'
);
 #   DROP TYPE public.seller_type_enum;
       public          mykhailo_lozinskyi    false            z           1247    85922    sex_enum    TYPE     B   CREATE TYPE public.sex_enum AS ENUM (
    'female',
    'male'
);
    DROP TYPE public.sex_enum;
       public          mykhailo_lozinskyi    false            }           1247    85928    transmission_enum    TYPE     P   CREATE TYPE public.transmission_enum AS ENUM (
    'automatic',
    'manual'
);
 $   DROP TYPE public.transmission_enum;
       public          mykhailo_lozinskyi    false            �           1247    85934 
   url_domain    DOMAIN     �   CREATE DOMAIN public.url_domain AS character varying(2048)
	CONSTRAINT url_domain_check CHECK (((VALUE)::text ~ '^https?://[^\s/$.?#].[^\s]*$'::text));
    DROP DOMAIN public.url_domain;
       public          mykhailo_lozinskyi    false            �            1255    86214 (   check_estimation_date_trigger_function()    FUNCTION     7  CREATE FUNCTION public.check_estimation_date_trigger_function() RETURNS trigger
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
 ?   DROP FUNCTION public.check_estimation_date_trigger_function();
       public          postgres    false            �            1255    85936 &   check_purchase_date_trigger_function()    FUNCTION     �  CREATE FUNCTION public.check_purchase_date_trigger_function() RETURNS trigger
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
 =   DROP FUNCTION public.check_purchase_date_trigger_function();
       public          postgres    false            �            1255    85937 $   check_repair_date_trigger_function()    FUNCTION     4  CREATE FUNCTION public.check_repair_date_trigger_function() RETURNS trigger
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
 ;   DROP FUNCTION public.check_repair_date_trigger_function();
       public          postgres    false                        1255    85938 "   check_sale_date_trigger_function()    FUNCTION     X  CREATE FUNCTION public.check_sale_date_trigger_function() RETURNS trigger
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
 9   DROP FUNCTION public.check_sale_date_trigger_function();
       public          postgres    false            �            1255    85939 $   update_updated_at_trigger_function()    FUNCTION     �   CREATE FUNCTION public.update_updated_at_trigger_function() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;
 ;   DROP FUNCTION public.update_updated_at_trigger_function();
       public          postgres    false            �            1259    85940    address    TABLE     
  CREATE TABLE public.address (
    address_id integer NOT NULL,
    city_id integer,
    street character varying(100),
    postal_code character varying(15),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
    DROP TABLE public.address;
       public         heap    mykhailo_lozinskyi    false            �            1259    85943    address_address_id_seq    SEQUENCE     �   CREATE SEQUENCE public.address_address_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.address_address_id_seq;
       public          mykhailo_lozinskyi    false    214            �           0    0    address_address_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.address_address_id_seq OWNED BY public.address.address_id;
          public          mykhailo_lozinskyi    false    215            �            1259    85944    person    TABLE     �  CREATE TABLE public.person (
    person_id integer NOT NULL,
    first_name public.person_name_domain NOT NULL,
    last_name public.person_name_domain NOT NULL,
    middle_name public.person_name_domain,
    birth_date date,
    sex public.sex_enum,
    email public.email_domain,
    CONSTRAINT person_birth_date_check CHECK (((birth_date >= (CURRENT_DATE - '100 years'::interval)) AND (birth_date <= (CURRENT_DATE - '16 years'::interval))))
);
    DROP TABLE public.person;
       public         heap    mykhailo_lozinskyi    false    880    880    880    890    872            �            1259    85950    buyer    TABLE     �   CREATE TABLE public.buyer (
    address_id integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
)
INHERITS (public.person);
    DROP TABLE public.buyer;
       public         heap    mykhailo_lozinskyi    false    880    216    880    872    890    880            �            1259    85957    car    TABLE     N  CREATE TABLE public.car (
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
    DROP TABLE public.car;
       public         heap    mykhailo_lozinskyi    false    893            �            1259    85964    car_body_type    TABLE     H  CREATE TABLE public.car_body_type (
    car_body_type_id integer NOT NULL,
    name character varying(50),
    description text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT car_body_type_name_check CHECK (((name)::text ~ '^[A-Za-z0-9 -]+$'::text))
);
 !   DROP TABLE public.car_body_type;
       public         heap    mykhailo_lozinskyi    false            �            1259    85970 "   car_body_type_car_body_type_id_seq    SEQUENCE     �   CREATE SEQUENCE public.car_body_type_car_body_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 9   DROP SEQUENCE public.car_body_type_car_body_type_id_seq;
       public          mykhailo_lozinskyi    false    219            �           0    0 "   car_body_type_car_body_type_id_seq    SEQUENCE OWNED BY     i   ALTER SEQUENCE public.car_body_type_car_body_type_id_seq OWNED BY public.car_body_type.car_body_type_id;
          public          mykhailo_lozinskyi    false    220            �            1259    85971    car_make    TABLE     �   CREATE TABLE public.car_make (
    car_make_id integer NOT NULL,
    name character varying(255) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
    DROP TABLE public.car_make;
       public         heap    mykhailo_lozinskyi    false            �            1259    85974    car_make_care_make_id_seq    SEQUENCE     �   CREATE SEQUENCE public.car_make_care_make_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.car_make_care_make_id_seq;
       public          mykhailo_lozinskyi    false    221            �           0    0    car_make_care_make_id_seq    SEQUENCE OWNED BY     V   ALTER SEQUENCE public.car_make_care_make_id_seq OWNED BY public.car_make.car_make_id;
          public          mykhailo_lozinskyi    false    222            �            1259    85975    city    TABLE     5  CREATE TABLE public.city (
    city_id integer NOT NULL,
    country_id integer,
    name character varying(100) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT name_constraint CHECK (((name)::text ~ '^[A-Za-z ]+$'::text))
);
    DROP TABLE public.city;
       public         heap    mykhailo_lozinskyi    false            �            1259    85979    city_city_id_seq    SEQUENCE     �   CREATE SEQUENCE public.city_city_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 '   DROP SEQUENCE public.city_city_id_seq;
       public          mykhailo_lozinskyi    false    223            �           0    0    city_city_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE public.city_city_id_seq OWNED BY public.city.city_id;
          public          mykhailo_lozinskyi    false    224            �            1259    85980    color    TABLE     �  CREATE TABLE public.color (
    color_id integer NOT NULL,
    name character varying(50) NOT NULL,
    hex_code character varying(6),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT color_hex_code_check CHECK (((hex_code)::text ~ '^[0-9A-Fa-f]{6}$'::text)),
    CONSTRAINT color_name_check CHECK (((name)::text ~ '^[a-zA-Z-]+$'::text))
);
    DROP TABLE public.color;
       public         heap    mykhailo_lozinskyi    false            �            1259    85985    color_color_id_seq    SEQUENCE     �   CREATE SEQUENCE public.color_color_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.color_color_id_seq;
       public          mykhailo_lozinskyi    false    225            �           0    0    color_color_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE public.color_color_id_seq OWNED BY public.color.color_id;
          public          mykhailo_lozinskyi    false    226            �            1259    85986    country    TABLE       CREATE TABLE public.country (
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
    DROP TABLE public.country;
       public         heap    mykhailo_lozinskyi    false            �            1259    85992    country_country_id_seq    SEQUENCE     �   CREATE SEQUENCE public.country_country_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.country_country_id_seq;
       public          mykhailo_lozinskyi    false    227            �           0    0    country_country_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.country_country_id_seq OWNED BY public.country.country_id;
          public          mykhailo_lozinskyi    false    228            �            1259    85993    employee    TABLE     �  CREATE TABLE public.employee (
    position_id integer,
    salary public.non_negative_domain NOT NULL,
    hire_date date NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT employee_hire_date_check CHECK (((hire_date >= (CURRENT_DATE - '100 years'::interval)) AND (hire_date <= (CURRENT_DATE - '1 mon'::interval))))
)
INHERITS (public.person);
    DROP TABLE public.employee;
       public         heap    mykhailo_lozinskyi    false    876    880    880    880    890    872    216            �            1259    86185 
   estimation    TABLE     Z  CREATE TABLE public.estimation (
    estimation_id integer NOT NULL,
    car_vin character varying(17),
    price public.non_negative_domain NOT NULL,
    estimation_date date NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);
    DROP TABLE public.estimation;
       public         heap    postgres    false    876            �            1259    86184    estimation_estimation_id_seq    SEQUENCE     �   CREATE SEQUENCE public.estimation_estimation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.estimation_estimation_id_seq;
       public          postgres    false    240            �           0    0    estimation_estimation_id_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE public.estimation_estimation_id_seq OWNED BY public.estimation.estimation_id;
          public          postgres    false    239            �            1259    86000    person_person_id_seq    SEQUENCE     �   CREATE SEQUENCE public.person_person_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.person_person_id_seq;
       public          mykhailo_lozinskyi    false    216            �           0    0    person_person_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.person_person_id_seq OWNED BY public.person.person_id;
          public          mykhailo_lozinskyi    false    230            �            1259    86001    position    TABLE     �   CREATE TABLE public."position" (
    position_id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
    DROP TABLE public."position";
       public         heap    mykhailo_lozinskyi    false            �            1259    86006    position_position_id_seq    SEQUENCE     �   CREATE SEQUENCE public.position_position_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.position_position_id_seq;
       public          mykhailo_lozinskyi    false    231            �           0    0    position_position_id_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE public.position_position_id_seq OWNED BY public."position".position_id;
          public          mykhailo_lozinskyi    false    232            �            1259    86007    purchase    TABLE     �  CREATE TABLE public.purchase (
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
    DROP TABLE public.purchase;
       public         heap    mykhailo_lozinskyi    false    868    876    876            �            1259    86012    repair    TABLE     �  CREATE TABLE public.repair (
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
    DROP TABLE public.repair;
       public         heap    mykhailo_lozinskyi    false    876    884    868            �            1259    86017    repair_repair_id_seq    SEQUENCE     �   CREATE SEQUENCE public.repair_repair_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.repair_repair_id_seq;
       public          mykhailo_lozinskyi    false    234            �           0    0    repair_repair_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.repair_repair_id_seq OWNED BY public.repair.repair_id;
          public          mykhailo_lozinskyi    false    235            �            1259    86018    sale    TABLE     �  CREATE TABLE public.sale (
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
    DROP TABLE public.sale;
       public         heap    mykhailo_lozinskyi    false    868    876    876    876            �            1259    86023    seller    TABLE     O  CREATE TABLE public.seller (
    seller_id integer NOT NULL,
    name character varying(100) NOT NULL,
    type public.seller_type_enum,
    address_id integer,
    email public.email_domain,
    website_url public.url_domain,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
    DROP TABLE public.seller;
       public         heap    mykhailo_lozinskyi    false    872    887    896            �            1259    86028    seller_seller_id_seq    SEQUENCE     �   CREATE SEQUENCE public.seller_seller_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.seller_seller_id_seq;
       public          mykhailo_lozinskyi    false    237            �           0    0    seller_seller_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.seller_seller_id_seq OWNED BY public.seller.seller_id;
          public          mykhailo_lozinskyi    false    238            �           2604    86029    address address_id    DEFAULT     x   ALTER TABLE ONLY public.address ALTER COLUMN address_id SET DEFAULT nextval('public.address_address_id_seq'::regclass);
 A   ALTER TABLE public.address ALTER COLUMN address_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    215    214            �           2604    86030    buyer person_id    DEFAULT     s   ALTER TABLE ONLY public.buyer ALTER COLUMN person_id SET DEFAULT nextval('public.person_person_id_seq'::regclass);
 >   ALTER TABLE public.buyer ALTER COLUMN person_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    230    217            �           2604    86031    car_body_type car_body_type_id    DEFAULT     �   ALTER TABLE ONLY public.car_body_type ALTER COLUMN car_body_type_id SET DEFAULT nextval('public.car_body_type_car_body_type_id_seq'::regclass);
 M   ALTER TABLE public.car_body_type ALTER COLUMN car_body_type_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    220    219            �           2604    86032    car_make car_make_id    DEFAULT     }   ALTER TABLE ONLY public.car_make ALTER COLUMN car_make_id SET DEFAULT nextval('public.car_make_care_make_id_seq'::regclass);
 C   ALTER TABLE public.car_make ALTER COLUMN car_make_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    222    221            �           2604    86033    city city_id    DEFAULT     l   ALTER TABLE ONLY public.city ALTER COLUMN city_id SET DEFAULT nextval('public.city_city_id_seq'::regclass);
 ;   ALTER TABLE public.city ALTER COLUMN city_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    224    223            �           2604    86034    color color_id    DEFAULT     p   ALTER TABLE ONLY public.color ALTER COLUMN color_id SET DEFAULT nextval('public.color_color_id_seq'::regclass);
 =   ALTER TABLE public.color ALTER COLUMN color_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    226    225            �           2604    86035    country country_id    DEFAULT     x   ALTER TABLE ONLY public.country ALTER COLUMN country_id SET DEFAULT nextval('public.country_country_id_seq'::regclass);
 A   ALTER TABLE public.country ALTER COLUMN country_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    228    227            �           2604    86036    employee person_id    DEFAULT     v   ALTER TABLE ONLY public.employee ALTER COLUMN person_id SET DEFAULT nextval('public.person_person_id_seq'::regclass);
 A   ALTER TABLE public.employee ALTER COLUMN person_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    230    229            �           2604    86188    estimation estimation_id    DEFAULT     �   ALTER TABLE ONLY public.estimation ALTER COLUMN estimation_id SET DEFAULT nextval('public.estimation_estimation_id_seq'::regclass);
 G   ALTER TABLE public.estimation ALTER COLUMN estimation_id DROP DEFAULT;
       public          postgres    false    239    240    240            �           2604    86037    person person_id    DEFAULT     t   ALTER TABLE ONLY public.person ALTER COLUMN person_id SET DEFAULT nextval('public.person_person_id_seq'::regclass);
 ?   ALTER TABLE public.person ALTER COLUMN person_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    230    216            �           2604    86038    position position_id    DEFAULT     ~   ALTER TABLE ONLY public."position" ALTER COLUMN position_id SET DEFAULT nextval('public.position_position_id_seq'::regclass);
 E   ALTER TABLE public."position" ALTER COLUMN position_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    232    231            �           2604    86039    repair repair_id    DEFAULT     t   ALTER TABLE ONLY public.repair ALTER COLUMN repair_id SET DEFAULT nextval('public.repair_repair_id_seq'::regclass);
 ?   ALTER TABLE public.repair ALTER COLUMN repair_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    235    234            �           2604    86040    seller seller_id    DEFAULT     t   ALTER TABLE ONLY public.seller ALTER COLUMN seller_id SET DEFAULT nextval('public.seller_seller_id_seq'::regclass);
 ?   ALTER TABLE public.seller ALTER COLUMN seller_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    238    237            �          0    85940    address 
   TABLE DATA           c   COPY public.address (address_id, city_id, street, postal_code, created_at, updated_at) FROM stdin;
    public          mykhailo_lozinskyi    false    214   1�       �          0    85950    buyer 
   TABLE DATA           �   COPY public.buyer (person_id, first_name, last_name, middle_name, birth_date, sex, email, address_id, created_at, updated_at) FROM stdin;
    public          mykhailo_lozinskyi    false    217   N�       �          0    85957    car 
   TABLE DATA           �   COPY public.car (vin, manufacture_year, make_id, model, "trim", body_type_id, transmission, color_id, description, created_at, updated_at) FROM stdin;
    public          mykhailo_lozinskyi    false    218   k�       �          0    85964    car_body_type 
   TABLE DATA           d   COPY public.car_body_type (car_body_type_id, name, description, created_at, updated_at) FROM stdin;
    public          mykhailo_lozinskyi    false    219   ��       �          0    85971    car_make 
   TABLE DATA           M   COPY public.car_make (car_make_id, name, created_at, updated_at) FROM stdin;
    public          mykhailo_lozinskyi    false    221   ��       �          0    85975    city 
   TABLE DATA           Q   COPY public.city (city_id, country_id, name, created_at, updated_at) FROM stdin;
    public          mykhailo_lozinskyi    false    223   ��       �          0    85980    color 
   TABLE DATA           Q   COPY public.color (color_id, name, hex_code, created_at, updated_at) FROM stdin;
    public          mykhailo_lozinskyi    false    225   ��       �          0    85986    country 
   TABLE DATA           V   COPY public.country (country_id, name, iso, iso3, created_at, updated_at) FROM stdin;
    public          mykhailo_lozinskyi    false    227   ��       �          0    85993    employee 
   TABLE DATA           �   COPY public.employee (person_id, first_name, last_name, middle_name, birth_date, sex, email, position_id, salary, hire_date, created_at, updated_at) FROM stdin;
    public          mykhailo_lozinskyi    false    229   �       �          0    86185 
   estimation 
   TABLE DATA           l   COPY public.estimation (estimation_id, car_vin, price, estimation_date, created_at, updated_at) FROM stdin;
    public          postgres    false    240   6�       �          0    85944    person 
   TABLE DATA           g   COPY public.person (person_id, first_name, last_name, middle_name, birth_date, sex, email) FROM stdin;
    public          mykhailo_lozinskyi    false    216   S�       �          0    86001    position 
   TABLE DATA           \   COPY public."position" (position_id, name, description, created_at, updated_at) FROM stdin;
    public          mykhailo_lozinskyi    false    231   p�       �          0    86007    purchase 
   TABLE DATA           �   COPY public.purchase (car_vin, seller_id, employee_id, price, odometer, condition, description, car_image, purchase_date, created_at, updated_at, car_image_content_type) FROM stdin;
    public          mykhailo_lozinskyi    false    233   ��       �          0    86012    repair 
   TABLE DATA           �   COPY public.repair (repair_id, car_vin, employee_id, address_id, repair_type, cost, condition, description, repair_date, created_at, updated_at) FROM stdin;
    public          mykhailo_lozinskyi    false    234   ��       �          0    86018    sale 
   TABLE DATA           �   COPY public.sale (car_vin, buyer_id, employee_id, mmr, price, odometer, condition, car_image, description, sale_date, created_at, updated_at, car_image_content_type) FROM stdin;
    public          mykhailo_lozinskyi    false    236   ��       �          0    86023    seller 
   TABLE DATA           o   COPY public.seller (seller_id, name, type, address_id, email, website_url, created_at, updated_at) FROM stdin;
    public          mykhailo_lozinskyi    false    237   ��       �           0    0    address_address_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.address_address_id_seq', 29790, true);
          public          mykhailo_lozinskyi    false    215            �           0    0 "   car_body_type_car_body_type_id_seq    SEQUENCE SET     Q   SELECT pg_catalog.setval('public.car_body_type_car_body_type_id_seq', 77, true);
          public          mykhailo_lozinskyi    false    220            �           0    0    car_make_care_make_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.car_make_care_make_id_seq', 54, true);
          public          mykhailo_lozinskyi    false    222            �           0    0    city_city_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.city_city_id_seq', 35, true);
          public          mykhailo_lozinskyi    false    224            �           0    0    color_color_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.color_color_id_seq', 21, true);
          public          mykhailo_lozinskyi    false    226            �           0    0    country_country_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.country_country_id_seq', 6, true);
          public          mykhailo_lozinskyi    false    228            �           0    0    estimation_estimation_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.estimation_estimation_id_seq', 1, false);
          public          postgres    false    239            �           0    0    person_person_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.person_person_id_seq', 237, true);
          public          mykhailo_lozinskyi    false    230            �           0    0    position_position_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.position_position_id_seq', 5, true);
          public          mykhailo_lozinskyi    false    232            �           0    0    repair_repair_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.repair_repair_id_seq', 20, true);
          public          mykhailo_lozinskyi    false    235                        0    0    seller_seller_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.seller_seller_id_seq', 29697, true);
          public          mykhailo_lozinskyi    false    238            �           2606    86042    address address_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.address
    ADD CONSTRAINT address_pkey PRIMARY KEY (address_id);
 >   ALTER TABLE ONLY public.address DROP CONSTRAINT address_pkey;
       public            mykhailo_lozinskyi    false    214            �           2606    86044 $   car_body_type car_body_type_name_key 
   CONSTRAINT     _   ALTER TABLE ONLY public.car_body_type
    ADD CONSTRAINT car_body_type_name_key UNIQUE (name);
 N   ALTER TABLE ONLY public.car_body_type DROP CONSTRAINT car_body_type_name_key;
       public            mykhailo_lozinskyi    false    219            �           2606    86046     car_body_type car_body_type_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.car_body_type
    ADD CONSTRAINT car_body_type_pkey PRIMARY KEY (car_body_type_id);
 J   ALTER TABLE ONLY public.car_body_type DROP CONSTRAINT car_body_type_pkey;
       public            mykhailo_lozinskyi    false    219            �           2606    86048    car_make car_make_name_key 
   CONSTRAINT     U   ALTER TABLE ONLY public.car_make
    ADD CONSTRAINT car_make_name_key UNIQUE (name);
 D   ALTER TABLE ONLY public.car_make DROP CONSTRAINT car_make_name_key;
       public            mykhailo_lozinskyi    false    221            �           2606    86050    car_make car_make_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public.car_make
    ADD CONSTRAINT car_make_pkey PRIMARY KEY (car_make_id);
 @   ALTER TABLE ONLY public.car_make DROP CONSTRAINT car_make_pkey;
       public            mykhailo_lozinskyi    false    221            �           2606    86052    car car_pkey 
   CONSTRAINT     K   ALTER TABLE ONLY public.car
    ADD CONSTRAINT car_pkey PRIMARY KEY (vin);
 6   ALTER TABLE ONLY public.car DROP CONSTRAINT car_pkey;
       public            mykhailo_lozinskyi    false    218            �           2606    86054    city city_pkey 
   CONSTRAINT     Q   ALTER TABLE ONLY public.city
    ADD CONSTRAINT city_pkey PRIMARY KEY (city_id);
 8   ALTER TABLE ONLY public.city DROP CONSTRAINT city_pkey;
       public            mykhailo_lozinskyi    false    223                       2606    86056    color color_name_key 
   CONSTRAINT     O   ALTER TABLE ONLY public.color
    ADD CONSTRAINT color_name_key UNIQUE (name);
 >   ALTER TABLE ONLY public.color DROP CONSTRAINT color_name_key;
       public            mykhailo_lozinskyi    false    225                       2606    86058    color color_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.color
    ADD CONSTRAINT color_pkey PRIMARY KEY (color_id);
 :   ALTER TABLE ONLY public.color DROP CONSTRAINT color_pkey;
       public            mykhailo_lozinskyi    false    225                       2606    86060    country country_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.country
    ADD CONSTRAINT country_pkey PRIMARY KEY (country_id);
 >   ALTER TABLE ONLY public.country DROP CONSTRAINT country_pkey;
       public            mykhailo_lozinskyi    false    227                       2606    86192    estimation estimation_pkey 
   CONSTRAINT     c   ALTER TABLE ONLY public.estimation
    ADD CONSTRAINT estimation_pkey PRIMARY KEY (estimation_id);
 D   ALTER TABLE ONLY public.estimation DROP CONSTRAINT estimation_pkey;
       public            postgres    false    240            �           2606    86062    person person_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY public.person
    ADD CONSTRAINT person_pkey PRIMARY KEY (person_id);
 <   ALTER TABLE ONLY public.person DROP CONSTRAINT person_pkey;
       public            mykhailo_lozinskyi    false    216                       2606    86064    position position_pkey 
   CONSTRAINT     _   ALTER TABLE ONLY public."position"
    ADD CONSTRAINT position_pkey PRIMARY KEY (position_id);
 B   ALTER TABLE ONLY public."position" DROP CONSTRAINT position_pkey;
       public            mykhailo_lozinskyi    false    231                       2606    86066    purchase purchase_pkey 
   CONSTRAINT     Y   ALTER TABLE ONLY public.purchase
    ADD CONSTRAINT purchase_pkey PRIMARY KEY (car_vin);
 @   ALTER TABLE ONLY public.purchase DROP CONSTRAINT purchase_pkey;
       public            mykhailo_lozinskyi    false    233                       2606    86068    repair repair_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY public.repair
    ADD CONSTRAINT repair_pkey PRIMARY KEY (repair_id);
 <   ALTER TABLE ONLY public.repair DROP CONSTRAINT repair_pkey;
       public            mykhailo_lozinskyi    false    234                       2606    86070    sale sale_pkey 
   CONSTRAINT     Q   ALTER TABLE ONLY public.sale
    ADD CONSTRAINT sale_pkey PRIMARY KEY (car_vin);
 8   ALTER TABLE ONLY public.sale DROP CONSTRAINT sale_pkey;
       public            mykhailo_lozinskyi    false    236                       2606    86072    seller seller_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY public.seller
    ADD CONSTRAINT seller_pkey PRIMARY KEY (seller_id);
 <   ALTER TABLE ONLY public.seller DROP CONSTRAINT seller_pkey;
       public            mykhailo_lozinskyi    false    237            �           2606    86074    buyer unique_buyer_person_id 
   CONSTRAINT     \   ALTER TABLE ONLY public.buyer
    ADD CONSTRAINT unique_buyer_person_id UNIQUE (person_id);
 F   ALTER TABLE ONLY public.buyer DROP CONSTRAINT unique_buyer_person_id;
       public            mykhailo_lozinskyi    false    217                       2606    86076 &   country unique_country_iso3_constraint 
   CONSTRAINT     a   ALTER TABLE ONLY public.country
    ADD CONSTRAINT unique_country_iso3_constraint UNIQUE (iso3);
 P   ALTER TABLE ONLY public.country DROP CONSTRAINT unique_country_iso3_constraint;
       public            mykhailo_lozinskyi    false    227            	           2606    86078 %   country unique_country_iso_constraint 
   CONSTRAINT     _   ALTER TABLE ONLY public.country
    ADD CONSTRAINT unique_country_iso_constraint UNIQUE (iso);
 O   ALTER TABLE ONLY public.country DROP CONSTRAINT unique_country_iso_constraint;
       public            mykhailo_lozinskyi    false    227                       2606    86080 "   employee unique_employee_person_id 
   CONSTRAINT     b   ALTER TABLE ONLY public.employee
    ADD CONSTRAINT unique_employee_person_id UNIQUE (person_id);
 L   ALTER TABLE ONLY public.employee DROP CONSTRAINT unique_employee_person_id;
       public            mykhailo_lozinskyi    false    229            �           1259    107632    car_make_id_model_index    INDEX     Q   CREATE INDEX car_make_id_model_index ON public.car USING btree (make_id, model);
 +   DROP INDEX public.car_make_id_model_index;
       public            mykhailo_lozinskyi    false    218    218            �           1259    107633    car_make_name_index    INDEX     H   CREATE INDEX car_make_name_index ON public.car_make USING btree (name);
 '   DROP INDEX public.car_make_name_index;
       public            mykhailo_lozinskyi    false    221            *           2620    86081    address address_update_trigger    TRIGGER     �   CREATE TRIGGER address_update_trigger BEFORE UPDATE ON public.address FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();
 7   DROP TRIGGER address_update_trigger ON public.address;
       public          mykhailo_lozinskyi    false    214    254            +           2620    86082    buyer buyer_update_trigger    TRIGGER     �   CREATE TRIGGER buyer_update_trigger BEFORE UPDATE ON public.buyer FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();
 3   DROP TRIGGER buyer_update_trigger ON public.buyer;
       public          mykhailo_lozinskyi    false    254    217            -           2620    86083 *   car_body_type car_body_type_update_trigger    TRIGGER     �   CREATE TRIGGER car_body_type_update_trigger BEFORE UPDATE ON public.car_body_type FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();
 C   DROP TRIGGER car_body_type_update_trigger ON public.car_body_type;
       public          mykhailo_lozinskyi    false    254    219            .           2620    86084     car_make car_make_update_trigger    TRIGGER     �   CREATE TRIGGER car_make_update_trigger BEFORE UPDATE ON public.car_make FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();
 9   DROP TRIGGER car_make_update_trigger ON public.car_make;
       public          mykhailo_lozinskyi    false    221    254            ,           2620    86085    car car_update_trigger    TRIGGER     �   CREATE TRIGGER car_update_trigger BEFORE UPDATE ON public.car FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();
 /   DROP TRIGGER car_update_trigger ON public.car;
       public          mykhailo_lozinskyi    false    218    254            :           2620    86215 (   estimation check_estimation_date_trigger    TRIGGER     �   CREATE TRIGGER check_estimation_date_trigger BEFORE INSERT OR UPDATE ON public.estimation FOR EACH ROW EXECUTE FUNCTION public.check_estimation_date_trigger_function();
 A   DROP TRIGGER check_estimation_date_trigger ON public.estimation;
       public          postgres    false    240    255            3           2620    86086 $   purchase check_purchase_date_trigger    TRIGGER     �   CREATE TRIGGER check_purchase_date_trigger BEFORE INSERT OR UPDATE ON public.purchase FOR EACH ROW EXECUTE FUNCTION public.check_purchase_date_trigger_function();
 =   DROP TRIGGER check_purchase_date_trigger ON public.purchase;
       public          mykhailo_lozinskyi    false    233    241            5           2620    86087     repair check_repair_date_trigger    TRIGGER     �   CREATE TRIGGER check_repair_date_trigger BEFORE INSERT OR UPDATE ON public.repair FOR EACH ROW EXECUTE FUNCTION public.check_repair_date_trigger_function();
 9   DROP TRIGGER check_repair_date_trigger ON public.repair;
       public          mykhailo_lozinskyi    false    242    234            7           2620    86088    sale check_sale_date_trigger    TRIGGER     �   CREATE TRIGGER check_sale_date_trigger BEFORE INSERT OR UPDATE ON public.sale FOR EACH ROW EXECUTE FUNCTION public.check_sale_date_trigger_function();
 5   DROP TRIGGER check_sale_date_trigger ON public.sale;
       public          mykhailo_lozinskyi    false    236    256            /           2620    86089    city city_update_trigger    TRIGGER     �   CREATE TRIGGER city_update_trigger BEFORE UPDATE ON public.city FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();
 1   DROP TRIGGER city_update_trigger ON public.city;
       public          mykhailo_lozinskyi    false    223    254            0           2620    86090    color color_update_trigger    TRIGGER     �   CREATE TRIGGER color_update_trigger BEFORE UPDATE ON public.color FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();
 3   DROP TRIGGER color_update_trigger ON public.color;
       public          mykhailo_lozinskyi    false    254    225            1           2620    86091    country country_update_trigger    TRIGGER     �   CREATE TRIGGER country_update_trigger BEFORE UPDATE ON public.country FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();
 7   DROP TRIGGER country_update_trigger ON public.country;
       public          mykhailo_lozinskyi    false    227    254            2           2620    86092     employee employee_update_trigger    TRIGGER     �   CREATE TRIGGER employee_update_trigger BEFORE UPDATE ON public.employee FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();
 9   DROP TRIGGER employee_update_trigger ON public.employee;
       public          mykhailo_lozinskyi    false    229    254            ;           2620    86217 $   estimation estimation_update_trigger    TRIGGER     �   CREATE TRIGGER estimation_update_trigger BEFORE UPDATE ON public.estimation FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();
 =   DROP TRIGGER estimation_update_trigger ON public.estimation;
       public          postgres    false    254    240            4           2620    86094     purchase purchase_update_trigger    TRIGGER     �   CREATE TRIGGER purchase_update_trigger BEFORE UPDATE ON public.purchase FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();
 9   DROP TRIGGER purchase_update_trigger ON public.purchase;
       public          mykhailo_lozinskyi    false    233    254            6           2620    86095    repair repair_update_trigger    TRIGGER     �   CREATE TRIGGER repair_update_trigger BEFORE UPDATE ON public.repair FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();
 5   DROP TRIGGER repair_update_trigger ON public.repair;
       public          mykhailo_lozinskyi    false    254    234            8           2620    86096    sale sale_update_trigger    TRIGGER     �   CREATE TRIGGER sale_update_trigger BEFORE UPDATE ON public.sale FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();
 1   DROP TRIGGER sale_update_trigger ON public.sale;
       public          mykhailo_lozinskyi    false    236    254            9           2620    86097    seller seller_update_trigger    TRIGGER     �   CREATE TRIGGER seller_update_trigger BEFORE UPDATE ON public.seller FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_trigger_function();
 5   DROP TRIGGER seller_update_trigger ON public.seller;
       public          mykhailo_lozinskyi    false    254    237                       2606    86098    address address_city_id_fkey    FK CONSTRAINT        ALTER TABLE ONLY public.address
    ADD CONSTRAINT address_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.city(city_id);
 F   ALTER TABLE ONLY public.address DROP CONSTRAINT address_city_id_fkey;
       public          mykhailo_lozinskyi    false    214    223    3327                       2606    86103    buyer buyer_address_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.buyer
    ADD CONSTRAINT buyer_address_id_fkey FOREIGN KEY (address_id) REFERENCES public.address(address_id);
 E   ALTER TABLE ONLY public.buyer DROP CONSTRAINT buyer_address_id_fkey;
       public          mykhailo_lozinskyi    false    217    214    3309                       2606    86108    car car_body_type_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.car
    ADD CONSTRAINT car_body_type_id_fkey FOREIGN KEY (body_type_id) REFERENCES public.car_body_type(car_body_type_id);
 C   ALTER TABLE ONLY public.car DROP CONSTRAINT car_body_type_id_fkey;
       public          mykhailo_lozinskyi    false    219    3320    218                       2606    86113    car car_color_id_fkey    FK CONSTRAINT     {   ALTER TABLE ONLY public.car
    ADD CONSTRAINT car_color_id_fkey FOREIGN KEY (color_id) REFERENCES public.color(color_id);
 ?   ALTER TABLE ONLY public.car DROP CONSTRAINT car_color_id_fkey;
       public          mykhailo_lozinskyi    false    218    225    3331                       2606    86118    car car_make_id_fkey    FK CONSTRAINT        ALTER TABLE ONLY public.car
    ADD CONSTRAINT car_make_id_fkey FOREIGN KEY (make_id) REFERENCES public.car_make(car_make_id);
 >   ALTER TABLE ONLY public.car DROP CONSTRAINT car_make_id_fkey;
       public          mykhailo_lozinskyi    false    3325    221    218                       2606    86123    city city_country_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.city
    ADD CONSTRAINT city_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.country(country_id);
 C   ALTER TABLE ONLY public.city DROP CONSTRAINT city_country_id_fkey;
       public          mykhailo_lozinskyi    false    3333    227    223                       2606    86128 "   employee employee_position_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_position_id_fkey FOREIGN KEY (position_id) REFERENCES public."position"(position_id);
 L   ALTER TABLE ONLY public.employee DROP CONSTRAINT employee_position_id_fkey;
       public          mykhailo_lozinskyi    false    231    3341    229            )           2606    86193 "   estimation estimation_car_vin_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.estimation
    ADD CONSTRAINT estimation_car_vin_fkey FOREIGN KEY (car_vin) REFERENCES public.car(vin);
 L   ALTER TABLE ONLY public.estimation DROP CONSTRAINT estimation_car_vin_fkey;
       public          postgres    false    218    240    3316                       2606    86133    purchase purchase_car_vin_fkey    FK CONSTRAINT     |   ALTER TABLE ONLY public.purchase
    ADD CONSTRAINT purchase_car_vin_fkey FOREIGN KEY (car_vin) REFERENCES public.car(vin);
 H   ALTER TABLE ONLY public.purchase DROP CONSTRAINT purchase_car_vin_fkey;
       public          mykhailo_lozinskyi    false    233    3316    218                        2606    86138 "   purchase purchase_employee_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.purchase
    ADD CONSTRAINT purchase_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(person_id);
 L   ALTER TABLE ONLY public.purchase DROP CONSTRAINT purchase_employee_id_fkey;
       public          mykhailo_lozinskyi    false    229    233    3339            !           2606    86143     purchase purchase_seller_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.purchase
    ADD CONSTRAINT purchase_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.seller(seller_id);
 J   ALTER TABLE ONLY public.purchase DROP CONSTRAINT purchase_seller_id_fkey;
       public          mykhailo_lozinskyi    false    233    237    3349            "           2606    86148    repair repair_address_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.repair
    ADD CONSTRAINT repair_address_id_fkey FOREIGN KEY (address_id) REFERENCES public.address(address_id);
 G   ALTER TABLE ONLY public.repair DROP CONSTRAINT repair_address_id_fkey;
       public          mykhailo_lozinskyi    false    214    234    3309            #           2606    86153    repair repair_car_vin_fkey    FK CONSTRAINT     x   ALTER TABLE ONLY public.repair
    ADD CONSTRAINT repair_car_vin_fkey FOREIGN KEY (car_vin) REFERENCES public.car(vin);
 D   ALTER TABLE ONLY public.repair DROP CONSTRAINT repair_car_vin_fkey;
       public          mykhailo_lozinskyi    false    234    218    3316            $           2606    86158    repair repair_employee_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.repair
    ADD CONSTRAINT repair_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(person_id);
 H   ALTER TABLE ONLY public.repair DROP CONSTRAINT repair_employee_id_fkey;
       public          mykhailo_lozinskyi    false    3339    229    234            %           2606    86163    sale sale_buyer_id_fkey    FK CONSTRAINT     ~   ALTER TABLE ONLY public.sale
    ADD CONSTRAINT sale_buyer_id_fkey FOREIGN KEY (buyer_id) REFERENCES public.buyer(person_id);
 A   ALTER TABLE ONLY public.sale DROP CONSTRAINT sale_buyer_id_fkey;
       public          mykhailo_lozinskyi    false    217    236    3313            &           2606    86168    sale sale_car_vin_fkey    FK CONSTRAINT     t   ALTER TABLE ONLY public.sale
    ADD CONSTRAINT sale_car_vin_fkey FOREIGN KEY (car_vin) REFERENCES public.car(vin);
 @   ALTER TABLE ONLY public.sale DROP CONSTRAINT sale_car_vin_fkey;
       public          mykhailo_lozinskyi    false    236    3316    218            '           2606    86173    sale sale_employee_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.sale
    ADD CONSTRAINT sale_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(person_id);
 D   ALTER TABLE ONLY public.sale DROP CONSTRAINT sale_employee_id_fkey;
       public          mykhailo_lozinskyi    false    3339    229    236            (           2606    86178    seller seller_address_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.seller
    ADD CONSTRAINT seller_address_id_fkey FOREIGN KEY (address_id) REFERENCES public.address(address_id);
 G   ALTER TABLE ONLY public.seller DROP CONSTRAINT seller_address_id_fkey;
       public          mykhailo_lozinskyi    false    3309    214    237            �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �     