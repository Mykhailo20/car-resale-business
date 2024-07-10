PGDMP     "                    |           car_resale_business_OLAP    15.2    15.2 [    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    58493    car_resale_business_OLAP    DATABASE     �   CREATE DATABASE "car_resale_business_OLAP" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Ukrainian_Ukraine.1251';
 *   DROP DATABASE "car_resale_business_OLAP";
                mykhailo_lozinskyi    false            �           0    0 #   DATABASE "car_resale_business_OLAP"    COMMENT     �   COMMENT ON DATABASE "car_resale_business_OLAP" IS 'OLAP database for car resale business (educational subject - Data Warehouse)';
                   mykhailo_lozinskyi    false    3476            v           1247    58640    age_group_enum    TYPE     �   CREATE TYPE public.age_group_enum AS ENUM (
    'teenager',
    'young_adult',
    'adult',
    'middle_aged_adult',
    'senior'
);
 !   DROP TYPE public.age_group_enum;
       public          mykhailo_lozinskyi    false            �           1247    58498    car_condition_domain    DOMAIN     �   CREATE DOMAIN public.car_condition_domain AS numeric(2,1)
	CONSTRAINT car_condition_domain_check CHECK (((VALUE >= 1.0) AND (VALUE <= 5.0)));
 )   DROP DOMAIN public.car_condition_domain;
       public          mykhailo_lozinskyi    false            �           1247    60014    fact_name_enum    TYPE     X   CREATE TYPE public.fact_name_enum AS ENUM (
    'purchase',
    'repair',
    'sale'
);
 !   DROP TYPE public.fact_name_enum;
       public          postgres    false            V           1247    58495    non_negative_domain    DOMAIN     p   CREATE DOMAIN public.non_negative_domain AS integer
	CONSTRAINT non_negative_domain_check CHECK ((VALUE >= 0));
 (   DROP DOMAIN public.non_negative_domain;
       public          mykhailo_lozinskyi    false            Z           1247    58504    percentage_domain    DOMAIN     �   CREATE DOMAIN public.percentage_domain AS numeric(5,2)
	CONSTRAINT percentage_domain_check CHECK (((VALUE >= (0)::numeric) AND (VALUE <= (100)::numeric)));
 &   DROP DOMAIN public.percentage_domain;
       public          mykhailo_lozinskyi    false            ^           1247    58536    person_age_domain    DOMAIN     �   CREATE DOMAIN public.person_age_domain AS integer
	CONSTRAINT person_age_domain_check CHECK (((VALUE >= 16) AND (VALUE <= 100)));
 &   DROP DOMAIN public.person_age_domain;
       public          mykhailo_lozinskyi    false            b           1247    58501    person_name_domain    DOMAIN     �   CREATE DOMAIN public.person_name_domain AS character varying(50)
	CONSTRAINT person_name_check CHECK (((VALUE)::text ~ '^[A-Za-z]+$'::text));
 '   DROP DOMAIN public.person_name_domain;
       public          mykhailo_lozinskyi    false            y           1247    58566    repair_type_enum    TYPE     �   CREATE TYPE public.repair_type_enum AS ENUM (
    'painting',
    'mechanical_repair',
    'body_repair',
    'electrical_repair'
);
 #   DROP TYPE public.repair_type_enum;
       public          mykhailo_lozinskyi    false            |           1247    58576    seller_type_enum    TYPE     �   CREATE TYPE public.seller_type_enum AS ENUM (
    'car_manufacturing_company',
    'financial_institution',
    'car_rental_company',
    'dealership',
    'individual'
);
 #   DROP TYPE public.seller_type_enum;
       public          mykhailo_lozinskyi    false                       1247    58657    sex_enum    TYPE     B   CREATE TYPE public.sex_enum AS ENUM (
    'female',
    'male'
);
    DROP TYPE public.sex_enum;
       public          mykhailo_lozinskyi    false            �           1247    58518    transmission_enum    TYPE     P   CREATE TYPE public.transmission_enum AS ENUM (
    'automatic',
    'manual'
);
 $   DROP TYPE public.transmission_enum;
       public          mykhailo_lozinskyi    false            �           1247    58539    week_day_enum    TYPE     z   CREATE TYPE public.week_day_enum AS ENUM (
    'mon',
    'tue',
    'wed',
    'thu',
    'fri',
    'sat',
    'sun'
);
     DROP TYPE public.week_day_enum;
       public          mykhailo_lozinskyi    false            �            1255    60022 +   update_employee_validity_trigger_function()    FUNCTION     �  CREATE FUNCTION public.update_employee_validity_trigger_function() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Update existing records with the same employee_oltp_id
    UPDATE dim_employee
    SET is_valid = 0, updated_at = CURRENT_TIMESTAMP
    WHERE employee_oltp_id = NEW.employee_oltp_id AND is_valid = 1;
    
    -- Set the new record as valid
    NEW.is_valid = 1;
    RETURN NEW;
END;
$$;
 B   DROP FUNCTION public.update_employee_validity_trigger_function();
       public          postgres    false            �            1255    60002 +   update_location_validity_trigger_function()    FUNCTION     �  CREATE FUNCTION public.update_location_validity_trigger_function() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Update existing records with the same address_oltp_id
    UPDATE dim_location
    SET is_valid = 0, updated_at = CURRENT_TIMESTAMP
    WHERE address_oltp_id = NEW.address_oltp_id AND is_valid = 1;
    
    -- Set the new record as valid
    NEW.is_valid = 1;
    RETURN NEW;
END;
$$;
 B   DROP FUNCTION public.update_location_validity_trigger_function();
       public          postgres    false            �            1259    58736 	   dim_buyer    TABLE     �   CREATE TABLE public.dim_buyer (
    buyer_id integer NOT NULL,
    first_name public.person_name_domain NOT NULL,
    age public.person_age_domain,
    age_group public.age_group_enum,
    sex public.sex_enum,
    buyer_oltp_id integer NOT NULL
);
    DROP TABLE public.dim_buyer;
       public         heap    mykhailo_lozinskyi    false    886    866    862    895            �            1259    58735    dim_buyer_buyer_id_seq    SEQUENCE     �   CREATE SEQUENCE public.dim_buyer_buyer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.dim_buyer_buyer_id_seq;
       public          mykhailo_lozinskyi    false    226            �           0    0    dim_buyer_buyer_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.dim_buyer_buyer_id_seq OWNED BY public.dim_buyer.buyer_id;
          public          mykhailo_lozinskyi    false    225            �            1259    58697    dim_car    TABLE     �  CREATE TABLE public.dim_car (
    vin character varying(17) NOT NULL,
    manufacture_year smallint,
    make character varying(255),
    model character varying(50),
    "trim" character varying(100),
    body character varying(50),
    transmission public.transmission_enum,
    color character varying(50),
    CONSTRAINT dim_car_body_check CHECK (((vin)::text ~ '^[A-Za-z0-9 -]+$'::text)),
    CONSTRAINT dim_car_color_check CHECK (((color)::text ~ '^[a-zA-Z-]+$'::text)),
    CONSTRAINT dim_car_make_check CHECK ((length((make)::text) > 0)),
    CONSTRAINT dim_car_manufacture_year_check CHECK ((manufacture_year >= 1900)),
    CONSTRAINT dim_car_vin_check CHECK (((vin)::text ~ '^[A-Z0-9]{17}$'::text))
);
    DROP TABLE public.dim_car;
       public         heap    mykhailo_lozinskyi    false    898            �            1259    58729    dim_car_repair_type    TABLE     z   CREATE TABLE public.dim_car_repair_type (
    repair_type_id integer NOT NULL,
    repair_type public.repair_type_enum
);
 '   DROP TABLE public.dim_car_repair_type;
       public         heap    mykhailo_lozinskyi    false    889            �            1259    58728 &   dim_car_repair_type_repair_type_id_seq    SEQUENCE     �   CREATE SEQUENCE public.dim_car_repair_type_repair_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 =   DROP SEQUENCE public.dim_car_repair_type_repair_type_id_seq;
       public          mykhailo_lozinskyi    false    224            �           0    0 &   dim_car_repair_type_repair_type_id_seq    SEQUENCE OWNED BY     q   ALTER SEQUENCE public.dim_car_repair_type_repair_type_id_seq OWNED BY public.dim_car_repair_type.repair_type_id;
          public          mykhailo_lozinskyi    false    223            �            1259    58718    dim_date    TABLE     >  CREATE TABLE public.dim_date (
    date_id integer NOT NULL,
    date date,
    year smallint,
    month smallint,
    day smallint,
    week_day public.week_day_enum,
    date_oltp_vin character varying(17) NOT NULL,
    fact_name public.fact_name_enum NOT NULL,
    fact_oltp_id integer,
    CONSTRAINT dim_date_date_check CHECK ((date >= '1900-01-01'::date)),
    CONSTRAINT dim_date_day_check CHECK (((day >= 1) AND (day <= 31))),
    CONSTRAINT dim_date_month_check CHECK (((month >= 1) AND (month <= 12))),
    CONSTRAINT dim_date_year_check CHECK ((year >= 1900))
);
    DROP TABLE public.dim_date;
       public         heap    mykhailo_lozinskyi    false    901    922            �            1259    58717    dim_date_date_id_seq    SEQUENCE     �   CREATE SEQUENCE public.dim_date_date_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.dim_date_date_id_seq;
       public          mykhailo_lozinskyi    false    222            �           0    0    dim_date_date_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.dim_date_date_id_seq OWNED BY public.dim_date.date_id;
          public          mykhailo_lozinskyi    false    221            �            1259    58709    dim_employee    TABLE     �  CREATE TABLE public.dim_employee (
    employee_id integer NOT NULL,
    first_name public.person_name_domain NOT NULL,
    age public.person_age_domain,
    age_group public.age_group_enum,
    sex public.sex_enum,
    salary public.non_negative_domain,
    work_experience public.non_negative_domain,
    employee_oltp_id integer NOT NULL,
    is_valid integer,
    updated_at timestamp without time zone
);
     DROP TABLE public.dim_employee;
       public         heap    mykhailo_lozinskyi    false    862    854    854    895    866    886            �            1259    58708    dim_employee_employee_id_seq    SEQUENCE     �   CREATE SEQUENCE public.dim_employee_employee_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.dim_employee_employee_id_seq;
       public          mykhailo_lozinskyi    false    220            �           0    0    dim_employee_employee_id_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE public.dim_employee_employee_id_seq OWNED BY public.dim_employee.employee_id;
          public          mykhailo_lozinskyi    false    219            �            1259    58689    dim_location    TABLE     �  CREATE TABLE public.dim_location (
    location_id integer NOT NULL,
    country character varying(64),
    city character varying(100),
    address_oltp_id integer NOT NULL,
    is_valid integer,
    updated_at timestamp without time zone,
    CONSTRAINT dim_location_city_check CHECK (((city)::text ~ '^[A-Za-z -]+$'::text)),
    CONSTRAINT dim_location_country_check CHECK (((country)::text ~ '^[A-Za-z -]+$'::text))
);
     DROP TABLE public.dim_location;
       public         heap    mykhailo_lozinskyi    false            �            1259    58688    dim_location_location_id_seq    SEQUENCE     �   CREATE SEQUENCE public.dim_location_location_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.dim_location_location_id_seq;
       public          mykhailo_lozinskyi    false    217            �           0    0    dim_location_location_id_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE public.dim_location_location_id_seq OWNED BY public.dim_location.location_id;
          public          mykhailo_lozinskyi    false    216            �            1259    58663 
   dim_seller    TABLE     �   CREATE TABLE public.dim_seller (
    seller_id integer NOT NULL,
    name character varying(100) NOT NULL,
    type public.seller_type_enum,
    seller_oltp_id integer NOT NULL
);
    DROP TABLE public.dim_seller;
       public         heap    mykhailo_lozinskyi    false    892            �            1259    58662    dim_seller_seller_id_seq    SEQUENCE     �   CREATE SEQUENCE public.dim_seller_seller_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.dim_seller_seller_id_seq;
       public          mykhailo_lozinskyi    false    215            �           0    0    dim_seller_seller_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.dim_seller_seller_id_seq OWNED BY public.dim_seller.seller_id;
          public          mykhailo_lozinskyi    false    214            �            1259    58788    fact_car_purchase    TABLE     �  CREATE TABLE public.fact_car_purchase (
    car_vin character varying(17) NOT NULL,
    seller_id integer NOT NULL,
    employee_id integer NOT NULL,
    location_id integer NOT NULL,
    date_id integer NOT NULL,
    price public.non_negative_domain,
    car_years public.non_negative_domain,
    odometer public.non_negative_domain,
    condition public.car_condition_domain,
    employee_experience public.non_negative_domain
);
 %   DROP TABLE public.fact_car_purchase;
       public         heap    mykhailo_lozinskyi    false    854    854    854    854    904            �            1259    58820    fact_car_repair    TABLE     G  CREATE TABLE public.fact_car_repair (
    car_vin character varying(17) NOT NULL,
    employee_id integer NOT NULL,
    location_id integer NOT NULL,
    date_id integer NOT NULL,
    repair_type_id integer NOT NULL,
    cost public.non_negative_domain,
    condition_delta numeric(2,1),
    repair_oltp_id integer NOT NULL
);
 #   DROP TABLE public.fact_car_repair;
       public         heap    mykhailo_lozinskyi    false    854            �            1259    58852    fact_car_sale    TABLE     �  CREATE TABLE public.fact_car_sale (
    car_vin character varying(17) NOT NULL,
    buyer_id integer NOT NULL,
    employee_id integer NOT NULL,
    location_id integer NOT NULL,
    date_id integer NOT NULL,
    price public.non_negative_domain,
    gross_profit_amount integer,
    gross_profit_percentage public.percentage_domain,
    mmr public.non_negative_domain,
    price_margin integer,
    car_years public.non_negative_domain,
    odometer public.non_negative_domain,
    condition public.car_condition_domain,
    employee_experience public.non_negative_domain,
    service_time public.non_negative_domain,
    service_cost public.non_negative_domain
);
 !   DROP TABLE public.fact_car_sale;
       public         heap    mykhailo_lozinskyi    false    854    858    854    854    854    904    854    854    854            �           2604    58739    dim_buyer buyer_id    DEFAULT     x   ALTER TABLE ONLY public.dim_buyer ALTER COLUMN buyer_id SET DEFAULT nextval('public.dim_buyer_buyer_id_seq'::regclass);
 A   ALTER TABLE public.dim_buyer ALTER COLUMN buyer_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    226    225    226            �           2604    58732 "   dim_car_repair_type repair_type_id    DEFAULT     �   ALTER TABLE ONLY public.dim_car_repair_type ALTER COLUMN repair_type_id SET DEFAULT nextval('public.dim_car_repair_type_repair_type_id_seq'::regclass);
 Q   ALTER TABLE public.dim_car_repair_type ALTER COLUMN repair_type_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    223    224    224            �           2604    58721    dim_date date_id    DEFAULT     t   ALTER TABLE ONLY public.dim_date ALTER COLUMN date_id SET DEFAULT nextval('public.dim_date_date_id_seq'::regclass);
 ?   ALTER TABLE public.dim_date ALTER COLUMN date_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    221    222    222            �           2604    58712    dim_employee employee_id    DEFAULT     �   ALTER TABLE ONLY public.dim_employee ALTER COLUMN employee_id SET DEFAULT nextval('public.dim_employee_employee_id_seq'::regclass);
 G   ALTER TABLE public.dim_employee ALTER COLUMN employee_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    220    219    220            �           2604    58692    dim_location location_id    DEFAULT     �   ALTER TABLE ONLY public.dim_location ALTER COLUMN location_id SET DEFAULT nextval('public.dim_location_location_id_seq'::regclass);
 G   ALTER TABLE public.dim_location ALTER COLUMN location_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    216    217    217            �           2604    58666    dim_seller seller_id    DEFAULT     |   ALTER TABLE ONLY public.dim_seller ALTER COLUMN seller_id SET DEFAULT nextval('public.dim_seller_seller_id_seq'::regclass);
 C   ALTER TABLE public.dim_seller ALTER COLUMN seller_id DROP DEFAULT;
       public          mykhailo_lozinskyi    false    215    214    215            �          0    58736 	   dim_buyer 
   TABLE DATA           ]   COPY public.dim_buyer (buyer_id, first_name, age, age_group, sex, buyer_oltp_id) FROM stdin;
    public          mykhailo_lozinskyi    false    226   W�       �          0    58697    dim_car 
   TABLE DATA           h   COPY public.dim_car (vin, manufacture_year, make, model, "trim", body, transmission, color) FROM stdin;
    public          mykhailo_lozinskyi    false    218   t�       �          0    58729    dim_car_repair_type 
   TABLE DATA           J   COPY public.dim_car_repair_type (repair_type_id, repair_type) FROM stdin;
    public          mykhailo_lozinskyi    false    224   ��       �          0    58718    dim_date 
   TABLE DATA           u   COPY public.dim_date (date_id, date, year, month, day, week_day, date_oltp_vin, fact_name, fact_oltp_id) FROM stdin;
    public          mykhailo_lozinskyi    false    222   ��       �          0    58709    dim_employee 
   TABLE DATA           �   COPY public.dim_employee (employee_id, first_name, age, age_group, sex, salary, work_experience, employee_oltp_id, is_valid, updated_at) FROM stdin;
    public          mykhailo_lozinskyi    false    220   ˆ       �          0    58689    dim_location 
   TABLE DATA           i   COPY public.dim_location (location_id, country, city, address_oltp_id, is_valid, updated_at) FROM stdin;
    public          mykhailo_lozinskyi    false    217   �       �          0    58663 
   dim_seller 
   TABLE DATA           K   COPY public.dim_seller (seller_id, name, type, seller_oltp_id) FROM stdin;
    public          mykhailo_lozinskyi    false    215   �       �          0    58788    fact_car_purchase 
   TABLE DATA           �   COPY public.fact_car_purchase (car_vin, seller_id, employee_id, location_id, date_id, price, car_years, odometer, condition, employee_experience) FROM stdin;
    public          mykhailo_lozinskyi    false    227   "�       �          0    58820    fact_car_repair 
   TABLE DATA           �   COPY public.fact_car_repair (car_vin, employee_id, location_id, date_id, repair_type_id, cost, condition_delta, repair_oltp_id) FROM stdin;
    public          mykhailo_lozinskyi    false    228   ?�       �          0    58852    fact_car_sale 
   TABLE DATA           �   COPY public.fact_car_sale (car_vin, buyer_id, employee_id, location_id, date_id, price, gross_profit_amount, gross_profit_percentage, mmr, price_margin, car_years, odometer, condition, employee_experience, service_time, service_cost) FROM stdin;
    public          mykhailo_lozinskyi    false    229   \�       �           0    0    dim_buyer_buyer_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.dim_buyer_buyer_id_seq', 1, false);
          public          mykhailo_lozinskyi    false    225            �           0    0 &   dim_car_repair_type_repair_type_id_seq    SEQUENCE SET     U   SELECT pg_catalog.setval('public.dim_car_repair_type_repair_type_id_seq', 1, false);
          public          mykhailo_lozinskyi    false    223            �           0    0    dim_date_date_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.dim_date_date_id_seq', 1, false);
          public          mykhailo_lozinskyi    false    221            �           0    0    dim_employee_employee_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.dim_employee_employee_id_seq', 1, false);
          public          mykhailo_lozinskyi    false    219            �           0    0    dim_location_location_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.dim_location_location_id_seq', 1, false);
          public          mykhailo_lozinskyi    false    216            �           0    0    dim_seller_seller_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.dim_seller_seller_id_seq', 1, false);
          public          mykhailo_lozinskyi    false    214            �           2606    58743    dim_buyer dim_buyer_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.dim_buyer
    ADD CONSTRAINT dim_buyer_pkey PRIMARY KEY (buyer_id);
 B   ALTER TABLE ONLY public.dim_buyer DROP CONSTRAINT dim_buyer_pkey;
       public            mykhailo_lozinskyi    false    226            �           2606    58707    dim_car dim_car_pkey 
   CONSTRAINT     S   ALTER TABLE ONLY public.dim_car
    ADD CONSTRAINT dim_car_pkey PRIMARY KEY (vin);
 >   ALTER TABLE ONLY public.dim_car DROP CONSTRAINT dim_car_pkey;
       public            mykhailo_lozinskyi    false    218            �           2606    58734 ,   dim_car_repair_type dim_car_repair_type_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.dim_car_repair_type
    ADD CONSTRAINT dim_car_repair_type_pkey PRIMARY KEY (repair_type_id);
 V   ALTER TABLE ONLY public.dim_car_repair_type DROP CONSTRAINT dim_car_repair_type_pkey;
       public            mykhailo_lozinskyi    false    224            �           2606    58727    dim_date dim_date_pkey 
   CONSTRAINT     Y   ALTER TABLE ONLY public.dim_date
    ADD CONSTRAINT dim_date_pkey PRIMARY KEY (date_id);
 @   ALTER TABLE ONLY public.dim_date DROP CONSTRAINT dim_date_pkey;
       public            mykhailo_lozinskyi    false    222            �           2606    58716    dim_employee dim_employee_pkey 
   CONSTRAINT     e   ALTER TABLE ONLY public.dim_employee
    ADD CONSTRAINT dim_employee_pkey PRIMARY KEY (employee_id);
 H   ALTER TABLE ONLY public.dim_employee DROP CONSTRAINT dim_employee_pkey;
       public            mykhailo_lozinskyi    false    220            �           2606    58696    dim_location dim_location_pkey 
   CONSTRAINT     e   ALTER TABLE ONLY public.dim_location
    ADD CONSTRAINT dim_location_pkey PRIMARY KEY (location_id);
 H   ALTER TABLE ONLY public.dim_location DROP CONSTRAINT dim_location_pkey;
       public            mykhailo_lozinskyi    false    217            �           2606    58668    dim_seller dim_seller_pkey 
   CONSTRAINT     _   ALTER TABLE ONLY public.dim_seller
    ADD CONSTRAINT dim_seller_pkey PRIMARY KEY (seller_id);
 D   ALTER TABLE ONLY public.dim_seller DROP CONSTRAINT dim_seller_pkey;
       public            mykhailo_lozinskyi    false    215            �           2606    60033 *   dim_seller dim_seller_unique_oltp_id_check 
   CONSTRAINT     o   ALTER TABLE ONLY public.dim_seller
    ADD CONSTRAINT dim_seller_unique_oltp_id_check UNIQUE (seller_oltp_id);
 T   ALTER TABLE ONLY public.dim_seller DROP CONSTRAINT dim_seller_unique_oltp_id_check;
       public            mykhailo_lozinskyi    false    215            �           2606    58794 (   fact_car_purchase fact_car_purchase_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_purchase
    ADD CONSTRAINT fact_car_purchase_pkey PRIMARY KEY (car_vin, seller_id, employee_id, location_id, date_id);
 R   ALTER TABLE ONLY public.fact_car_purchase DROP CONSTRAINT fact_car_purchase_pkey;
       public            mykhailo_lozinskyi    false    227    227    227    227    227            �           2606    58826 $   fact_car_repair fact_car_repair_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_repair
    ADD CONSTRAINT fact_car_repair_pkey PRIMARY KEY (car_vin, employee_id, location_id, date_id, repair_type_id);
 N   ALTER TABLE ONLY public.fact_car_repair DROP CONSTRAINT fact_car_repair_pkey;
       public            mykhailo_lozinskyi    false    228    228    228    228    228            �           2606    58858     fact_car_sale fact_car_sale_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_sale
    ADD CONSTRAINT fact_car_sale_pkey PRIMARY KEY (car_vin, buyer_id, employee_id, location_id, date_id);
 J   ALTER TABLE ONLY public.fact_car_sale DROP CONSTRAINT fact_car_sale_pkey;
       public            mykhailo_lozinskyi    false    229    229    229    229    229            �           2620    60025 1   dim_employee dim_employee_update_validity_trigger    TRIGGER     �   CREATE TRIGGER dim_employee_update_validity_trigger BEFORE INSERT ON public.dim_employee FOR EACH ROW EXECUTE FUNCTION public.update_employee_validity_trigger_function();
 J   DROP TRIGGER dim_employee_update_validity_trigger ON public.dim_employee;
       public          mykhailo_lozinskyi    false    231    220            �           2620    60005 1   dim_location dim_location_update_validity_trigger    TRIGGER     �   CREATE TRIGGER dim_location_update_validity_trigger BEFORE INSERT ON public.dim_location FOR EACH ROW EXECUTE FUNCTION public.update_location_validity_trigger_function();
 J   DROP TRIGGER dim_location_update_validity_trigger ON public.dim_location;
       public          mykhailo_lozinskyi    false    217    230            �           2606    58795 0   fact_car_purchase fact_car_purchase_car_vin_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_purchase
    ADD CONSTRAINT fact_car_purchase_car_vin_fkey FOREIGN KEY (car_vin) REFERENCES public.dim_car(vin);
 Z   ALTER TABLE ONLY public.fact_car_purchase DROP CONSTRAINT fact_car_purchase_car_vin_fkey;
       public          mykhailo_lozinskyi    false    3281    218    227            �           2606    58815 0   fact_car_purchase fact_car_purchase_date_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_purchase
    ADD CONSTRAINT fact_car_purchase_date_id_fkey FOREIGN KEY (date_id) REFERENCES public.dim_date(date_id);
 Z   ALTER TABLE ONLY public.fact_car_purchase DROP CONSTRAINT fact_car_purchase_date_id_fkey;
       public          mykhailo_lozinskyi    false    3285    227    222            �           2606    58805 4   fact_car_purchase fact_car_purchase_employee_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_purchase
    ADD CONSTRAINT fact_car_purchase_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.dim_employee(employee_id);
 ^   ALTER TABLE ONLY public.fact_car_purchase DROP CONSTRAINT fact_car_purchase_employee_id_fkey;
       public          mykhailo_lozinskyi    false    3283    227    220            �           2606    58810 4   fact_car_purchase fact_car_purchase_location_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_purchase
    ADD CONSTRAINT fact_car_purchase_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.dim_location(location_id);
 ^   ALTER TABLE ONLY public.fact_car_purchase DROP CONSTRAINT fact_car_purchase_location_id_fkey;
       public          mykhailo_lozinskyi    false    3279    227    217            �           2606    58800 2   fact_car_purchase fact_car_purchase_seller_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_purchase
    ADD CONSTRAINT fact_car_purchase_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.dim_seller(seller_id);
 \   ALTER TABLE ONLY public.fact_car_purchase DROP CONSTRAINT fact_car_purchase_seller_id_fkey;
       public          mykhailo_lozinskyi    false    3275    215    227            �           2606    58827 ,   fact_car_repair fact_car_repair_car_vin_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_repair
    ADD CONSTRAINT fact_car_repair_car_vin_fkey FOREIGN KEY (car_vin) REFERENCES public.dim_car(vin);
 V   ALTER TABLE ONLY public.fact_car_repair DROP CONSTRAINT fact_car_repair_car_vin_fkey;
       public          mykhailo_lozinskyi    false    228    3281    218            �           2606    58842 ,   fact_car_repair fact_car_repair_date_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_repair
    ADD CONSTRAINT fact_car_repair_date_id_fkey FOREIGN KEY (date_id) REFERENCES public.dim_date(date_id);
 V   ALTER TABLE ONLY public.fact_car_repair DROP CONSTRAINT fact_car_repair_date_id_fkey;
       public          mykhailo_lozinskyi    false    222    228    3285            �           2606    58832 0   fact_car_repair fact_car_repair_employee_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_repair
    ADD CONSTRAINT fact_car_repair_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.dim_employee(employee_id);
 Z   ALTER TABLE ONLY public.fact_car_repair DROP CONSTRAINT fact_car_repair_employee_id_fkey;
       public          mykhailo_lozinskyi    false    228    220    3283            �           2606    58837 0   fact_car_repair fact_car_repair_location_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_repair
    ADD CONSTRAINT fact_car_repair_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.dim_location(location_id);
 Z   ALTER TABLE ONLY public.fact_car_repair DROP CONSTRAINT fact_car_repair_location_id_fkey;
       public          mykhailo_lozinskyi    false    3279    217    228            �           2606    58847 3   fact_car_repair fact_car_repair_repair_type_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_repair
    ADD CONSTRAINT fact_car_repair_repair_type_id_fkey FOREIGN KEY (repair_type_id) REFERENCES public.dim_car_repair_type(repair_type_id);
 ]   ALTER TABLE ONLY public.fact_car_repair DROP CONSTRAINT fact_car_repair_repair_type_id_fkey;
       public          mykhailo_lozinskyi    false    224    3287    228            �           2606    58864 )   fact_car_sale fact_car_sale_buyer_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_sale
    ADD CONSTRAINT fact_car_sale_buyer_id_fkey FOREIGN KEY (buyer_id) REFERENCES public.dim_buyer(buyer_id);
 S   ALTER TABLE ONLY public.fact_car_sale DROP CONSTRAINT fact_car_sale_buyer_id_fkey;
       public          mykhailo_lozinskyi    false    229    226    3289            �           2606    58859 (   fact_car_sale fact_car_sale_car_vin_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_sale
    ADD CONSTRAINT fact_car_sale_car_vin_fkey FOREIGN KEY (car_vin) REFERENCES public.dim_car(vin);
 R   ALTER TABLE ONLY public.fact_car_sale DROP CONSTRAINT fact_car_sale_car_vin_fkey;
       public          mykhailo_lozinskyi    false    229    3281    218            �           2606    58879 (   fact_car_sale fact_car_sale_date_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_sale
    ADD CONSTRAINT fact_car_sale_date_id_fkey FOREIGN KEY (date_id) REFERENCES public.dim_date(date_id);
 R   ALTER TABLE ONLY public.fact_car_sale DROP CONSTRAINT fact_car_sale_date_id_fkey;
       public          mykhailo_lozinskyi    false    229    222    3285            �           2606    58869 ,   fact_car_sale fact_car_sale_employee_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_sale
    ADD CONSTRAINT fact_car_sale_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.dim_employee(employee_id);
 V   ALTER TABLE ONLY public.fact_car_sale DROP CONSTRAINT fact_car_sale_employee_id_fkey;
       public          mykhailo_lozinskyi    false    220    229    3283            �           2606    58874 ,   fact_car_sale fact_car_sale_location_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fact_car_sale
    ADD CONSTRAINT fact_car_sale_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.dim_location(location_id);
 V   ALTER TABLE ONLY public.fact_car_sale DROP CONSTRAINT fact_car_sale_location_id_fkey;
       public          mykhailo_lozinskyi    false    229    3279    217            �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �     