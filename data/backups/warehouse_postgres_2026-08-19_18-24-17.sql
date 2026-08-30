--
-- PostgreSQL database dump
--

\restrict Ic01NNBAmrTH0VAU9O31gBWZJgfvP6ccWzs6tmUEXhCxlTzmJ1DbAo8GtpvSKkN

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: access_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.access_log (
    id integer NOT NULL,
    "timestamp" timestamp without time zone,
    username character varying(64) NOT NULL,
    warehouse_id character varying(20),
    action character varying(50) NOT NULL,
    ip_address character varying(45)
);


ALTER TABLE public.access_log OWNER TO postgres;

--
-- Name: access_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.access_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.access_log_id_seq OWNER TO postgres;

--
-- Name: access_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.access_log_id_seq OWNED BY public.access_log.id;


--
-- Name: ai_recommendations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ai_recommendations (
    id integer NOT NULL,
    "timestamp" timestamp without time zone,
    warehouse_id character varying(20) NOT NULL,
    item_id character varying(50),
    title character varying(100) NOT NULL,
    risk_level character varying(20),
    action_recommended character varying(100) NOT NULL,
    confidence_score integer,
    input_factors text,
    status character varying(20),
    decision_by character varying(64),
    decision_time timestamp without time zone,
    notes text,
    recommendation_type character varying(50),
    description text,
    priority character varying(20),
    score integer,
    confidence_or_reliability character varying(50),
    source_model character varying(50),
    source_entity_type character varying(50),
    source_entity_id character varying(50),
    recommended_action character varying(200),
    estimated_impact double precision,
    explanation text,
    supporting_metrics text,
    created_at timestamp without time zone NOT NULL,
    reviewed_at timestamp without time zone,
    reviewed_by character varying(64),
    review_notes text,
    expires_at timestamp without time zone,
    metadata text NOT NULL
);


ALTER TABLE public.ai_recommendations OWNER TO postgres;

--
-- Name: ai_recommendations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ai_recommendations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ai_recommendations_id_seq OWNER TO postgres;

--
-- Name: ai_recommendations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ai_recommendations_id_seq OWNED BY public.ai_recommendations.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: audit_ledger; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_ledger (
    id integer NOT NULL,
    "timestamp" timestamp without time zone,
    event_type character varying(50) NOT NULL,
    details text,
    prev_hash character varying(64) NOT NULL,
    hash character varying(64) NOT NULL
);


ALTER TABLE public.audit_ledger OWNER TO postgres;

--
-- Name: audit_ledger_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_ledger_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_ledger_id_seq OWNER TO postgres;

--
-- Name: audit_ledger_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_ledger_id_seq OWNED BY public.audit_ledger.id;


--
-- Name: backup_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.backup_records (
    id integer NOT NULL,
    backup_id character varying(64) NOT NULL,
    filename character varying(255) NOT NULL,
    created_at timestamp without time zone,
    size_bytes integer,
    sha256 character varying(64),
    status character varying(20) NOT NULL,
    storage_key character varying(255),
    error_message text,
    backup_type character varying(50),
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    storage_provider character varying(50),
    bucket character varying(255),
    checksum_algorithm character varying(20),
    verification_status character varying(50),
    verification_at timestamp without time zone,
    restore_test_status character varying(50),
    restore_test_at timestamp without time zone,
    retention_status character varying(50),
    initiated_by character varying(100),
    audit_ref character varying(255)
);


ALTER TABLE public.backup_records OWNER TO postgres;

--
-- Name: backup_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.backup_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.backup_records_id_seq OWNER TO postgres;

--
-- Name: backup_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.backup_records_id_seq OWNED BY public.backup_records.id;


--
-- Name: digital_twin_simulations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.digital_twin_simulations (
    id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    simulation_status character varying(20) NOT NULL,
    simulation_time_seconds double precision NOT NULL,
    speed_multiplier double precision NOT NULL,
    seed integer NOT NULL,
    mode character varying(20) NOT NULL,
    scenario_type character varying(30) NOT NULL,
    tick_count integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    started_at timestamp without time zone,
    paused_at timestamp without time zone,
    stopped_at timestamp without time zone,
    completed_at timestamp without time zone,
    error_message text,
    created_by character varying(64) NOT NULL
);


ALTER TABLE public.digital_twin_simulations OWNER TO postgres;

--
-- Name: digital_twin_simulations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.digital_twin_simulations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.digital_twin_simulations_id_seq OWNER TO postgres;

--
-- Name: digital_twin_simulations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.digital_twin_simulations_id_seq OWNED BY public.digital_twin_simulations.id;


--
-- Name: experiment_runs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.experiment_runs (
    id integer NOT NULL,
    experiment_id integer NOT NULL,
    repetition_number integer NOT NULL,
    random_seed integer NOT NULL,
    status character varying(20) NOT NULL,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    duration_seconds double precision,
    error_message text,
    metrics json,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.experiment_runs OWNER TO postgres;

--
-- Name: experiment_runs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.experiment_runs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.experiment_runs_id_seq OWNER TO postgres;

--
-- Name: experiment_runs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.experiment_runs_id_seq OWNED BY public.experiment_runs.id;


--
-- Name: experiments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.experiments (
    id integer NOT NULL,
    scenario_id integer NOT NULL,
    experiment_name character varying(150) NOT NULL,
    description text,
    status character varying(20) NOT NULL,
    algorithm_name character varying(50) NOT NULL,
    algorithm_version character varying(20) NOT NULL,
    configuration json NOT NULL,
    random_seed integer NOT NULL,
    repetitions integer NOT NULL,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    duration_seconds double precision,
    created_by character varying(64) NOT NULL,
    error_message text,
    metrics_summary json,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.experiments OWNER TO postgres;

--
-- Name: experiments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.experiments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.experiments_id_seq OWNER TO postgres;

--
-- Name: experiments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.experiments_id_seq OWNED BY public.experiments.id;


--
-- Name: health_thresholds; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.health_thresholds (
    id integer NOT NULL,
    key character varying(64) NOT NULL,
    value double precision NOT NULL,
    description character varying(255),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.health_thresholds OWNER TO postgres;

--
-- Name: health_thresholds_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.health_thresholds_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.health_thresholds_id_seq OWNER TO postgres;

--
-- Name: health_thresholds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.health_thresholds_id_seq OWNED BY public.health_thresholds.id;


--
-- Name: inventory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventory (
    id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    item_id character varying(20) NOT NULL,
    location_id character varying(50),
    on_hand integer NOT NULL,
    reserved integer NOT NULL,
    available integer NOT NULL,
    damaged integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.inventory OWNER TO postgres;

--
-- Name: inventory_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inventory_id_seq OWNER TO postgres;

--
-- Name: inventory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventory_id_seq OWNED BY public.inventory.id;


--
-- Name: inventory_reservations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventory_reservations (
    id integer NOT NULL,
    order_id character varying(20) NOT NULL,
    item_id character varying(20) NOT NULL,
    location_id character varying(50),
    reserved_qty integer NOT NULL,
    released_qty integer NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.inventory_reservations OWNER TO postgres;

--
-- Name: inventory_reservations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventory_reservations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inventory_reservations_id_seq OWNER TO postgres;

--
-- Name: inventory_reservations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventory_reservations_id_seq OWNED BY public.inventory_reservations.id;


--
-- Name: items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.items (
    id character varying(20) NOT NULL,
    name character varying(150) NOT NULL,
    category character varying(80),
    unit_cost double precision,
    lead_time_days integer,
    safety_stock integer,
    sku character varying(64),
    description text,
    unit character varying(20),
    weight_kg double precision,
    dimensions character varying(50),
    barcode character varying(64),
    is_active boolean,
    reorder_threshold integer,
    preferred_storage_type character varying(20),
    created_at timestamp without time zone
);


ALTER TABLE public.items OWNER TO postgres;

--
-- Name: notification_preferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification_preferences (
    id integer NOT NULL,
    user_id integer NOT NULL,
    category character varying(50) NOT NULL,
    in_app_enabled boolean NOT NULL,
    email_enabled boolean NOT NULL,
    min_severity character varying(20) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.notification_preferences OWNER TO postgres;

--
-- Name: notification_preferences_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notification_preferences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notification_preferences_id_seq OWNER TO postgres;

--
-- Name: notification_preferences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notification_preferences_id_seq OWNED BY public.notification_preferences.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    user_id integer NOT NULL,
    warehouse_id character varying(20),
    event_type character varying(50) NOT NULL,
    notification_type character varying(50) NOT NULL,
    title character varying(150) NOT NULL,
    message text NOT NULL,
    severity character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    channel character varying(20) NOT NULL,
    source_entity_type character varying(50),
    source_entity_id character varying(50),
    created_at timestamp without time zone NOT NULL,
    read_at timestamp without time zone,
    delivered_at timestamp without time zone,
    failed_at timestamp without time zone,
    retry_count integer NOT NULL,
    expires_at timestamp without time zone,
    metadata text NOT NULL,
    idempotency_key character varying(255)
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notifications_id_seq OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: order_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_events (
    id integer NOT NULL,
    order_id character varying(20) NOT NULL,
    "timestamp" timestamp without time zone,
    status character varying(30) NOT NULL,
    event_type character varying(50) NOT NULL,
    operator character varying(64),
    notes text
);


ALTER TABLE public.order_events OWNER TO postgres;

--
-- Name: order_events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_events_id_seq OWNER TO postgres;

--
-- Name: order_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_events_id_seq OWNED BY public.order_events.id;


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_items (
    id integer NOT NULL,
    order_id character varying(20) NOT NULL,
    item_id character varying(20) NOT NULL,
    requested_qty integer NOT NULL,
    reserved_qty integer NOT NULL,
    picked_qty integer NOT NULL,
    packed_qty integer NOT NULL,
    shipped_qty integer NOT NULL,
    status character varying(20) NOT NULL
);


ALTER TABLE public.order_items OWNER TO postgres;

--
-- Name: order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_items_id_seq OWNER TO postgres;

--
-- Name: order_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_items_id_seq OWNED BY public.order_items.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    id character varying(20) NOT NULL,
    customer_ref character varying(100) NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    status character varying(30) NOT NULL,
    priority character varying(20) NOT NULL,
    total_items integer NOT NULL,
    notes text,
    created_by character varying(64)
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- Name: otp_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.otp_records (
    id integer NOT NULL,
    user_id integer NOT NULL,
    purpose character varying(50) NOT NULL,
    code_hash character varying(255) NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    attempts integer NOT NULL,
    max_attempts integer NOT NULL,
    consumed_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    request_ip character varying(45),
    context_data text
);


ALTER TABLE public.otp_records OWNER TO postgres;

--
-- Name: otp_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.otp_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.otp_records_id_seq OWNER TO postgres;

--
-- Name: otp_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.otp_records_id_seq OWNED BY public.otp_records.id;


--
-- Name: packing_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.packing_records (
    id integer NOT NULL,
    order_id character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    operator character varying(64),
    package_count integer NOT NULL,
    weight_kg double precision,
    notes text
);


ALTER TABLE public.packing_records OWNER TO postgres;

--
-- Name: packing_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.packing_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.packing_records_id_seq OWNER TO postgres;

--
-- Name: packing_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.packing_records_id_seq OWNED BY public.packing_records.id;


--
-- Name: recovery_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recovery_codes (
    id integer NOT NULL,
    user_id integer NOT NULL,
    code_hash character varying(255) NOT NULL,
    used boolean NOT NULL,
    created_at timestamp without time zone,
    used_at timestamp without time zone
);


ALTER TABLE public.recovery_codes OWNER TO postgres;

--
-- Name: recovery_codes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.recovery_codes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recovery_codes_id_seq OWNER TO postgres;

--
-- Name: recovery_codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.recovery_codes_id_seq OWNED BY public.recovery_codes.id;


--
-- Name: recovery_credentials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recovery_credentials (
    id integer NOT NULL,
    user_id integer NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.recovery_credentials OWNER TO postgres;

--
-- Name: recovery_credentials_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.recovery_credentials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recovery_credentials_id_seq OWNER TO postgres;

--
-- Name: recovery_credentials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.recovery_credentials_id_seq OWNED BY public.recovery_credentials.id;


--
-- Name: robot_reservations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.robot_reservations (
    id integer NOT NULL,
    robot_id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    x integer NOT NULL,
    y integer NOT NULL,
    tick integer NOT NULL
);


ALTER TABLE public.robot_reservations OWNER TO postgres;

--
-- Name: robot_reservations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.robot_reservations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.robot_reservations_id_seq OWNER TO postgres;

--
-- Name: robot_reservations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.robot_reservations_id_seq OWNED BY public.robot_reservations.id;


--
-- Name: robot_routes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.robot_routes (
    id integer NOT NULL,
    robot_id integer NOT NULL,
    task_id integer,
    warehouse_id character varying(20) NOT NULL,
    start_x integer NOT NULL,
    start_y integer NOT NULL,
    goal_x integer NOT NULL,
    goal_y integer NOT NULL,
    algorithm character varying(30) NOT NULL,
    path_data text NOT NULL,
    distance double precision NOT NULL,
    cost double precision NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    completed_at timestamp without time zone
);


ALTER TABLE public.robot_routes OWNER TO postgres;

--
-- Name: robot_routes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.robot_routes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.robot_routes_id_seq OWNER TO postgres;

--
-- Name: robot_routes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.robot_routes_id_seq OWNED BY public.robot_routes.id;


--
-- Name: robot_telemetry; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.robot_telemetry (
    id integer NOT NULL,
    robot_id integer NOT NULL,
    event_type character varying(50) NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    x double precision NOT NULL,
    y double precision NOT NULL,
    battery double precision NOT NULL,
    status character varying(30) NOT NULL,
    task_id integer,
    metadata text NOT NULL
);


ALTER TABLE public.robot_telemetry OWNER TO postgres;

--
-- Name: robot_telemetry_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.robot_telemetry_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.robot_telemetry_id_seq OWNER TO postgres;

--
-- Name: robot_telemetry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.robot_telemetry_id_seq OWNED BY public.robot_telemetry.id;


--
-- Name: robots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.robots (
    id integer NOT NULL,
    robot_code character varying(30) NOT NULL,
    name character varying(100) NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    status character varying(30) NOT NULL,
    battery_level double precision NOT NULL,
    current_location_id character varying(50),
    current_x double precision NOT NULL,
    current_y double precision NOT NULL,
    target_location_id character varying(50),
    target_x double precision NOT NULL,
    target_y double precision NOT NULL,
    assigned_task_id integer,
    total_tasks_completed integer NOT NULL,
    total_distance double precision NOT NULL,
    total_operating_time double precision NOT NULL,
    utilization_percent double precision NOT NULL,
    failure_count integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    last_heartbeat_at timestamp without time zone NOT NULL,
    robot_type character varying(30) NOT NULL,
    max_payload double precision NOT NULL,
    max_speed double precision NOT NULL,
    enabled boolean NOT NULL,
    metadata text NOT NULL
);


ALTER TABLE public.robots OWNER TO postgres;

--
-- Name: robots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.robots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.robots_id_seq OWNER TO postgres;

--
-- Name: robots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.robots_id_seq OWNED BY public.robots.id;


--
-- Name: scenarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scenarios (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    warehouse_id character varying(20) NOT NULL,
    scenario_type character varying(30) NOT NULL,
    configuration json NOT NULL,
    random_seed integer NOT NULL,
    status character varying(20) NOT NULL,
    tags text NOT NULL,
    notes text,
    created_by character varying(64) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.scenarios OWNER TO postgres;

--
-- Name: scenarios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.scenarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.scenarios_id_seq OWNER TO postgres;

--
-- Name: scenarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.scenarios_id_seq OWNED BY public.scenarios.id;


--
-- Name: shipments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.shipments (
    id character varying(20) NOT NULL,
    order_id character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    tracking_reference character varying(100),
    carrier character varying(50),
    created_at timestamp without time zone,
    shipped_at timestamp without time zone,
    delivered_at timestamp without time zone
);


ALTER TABLE public.shipments OWNER TO postgres;

--
-- Name: shrinkage_flags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.shrinkage_flags (
    id integer NOT NULL,
    date date NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    item_id character varying(20) NOT NULL,
    item_name character varying(150),
    deviation_score double precision,
    expected_quantity double precision,
    actual_quantity double precision,
    discrepancy_quantity double precision,
    estimated_exposure double precision,
    severity character varying(20),
    likely_cause character varying(80),
    explanation text
);


ALTER TABLE public.shrinkage_flags OWNER TO postgres;

--
-- Name: shrinkage_flags_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.shrinkage_flags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.shrinkage_flags_id_seq OWNER TO postgres;

--
-- Name: shrinkage_flags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.shrinkage_flags_id_seq OWNED BY public.shrinkage_flags.id;


--
-- Name: simulation_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simulation_events (
    id integer NOT NULL,
    simulation_id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    event_type character varying(50) NOT NULL,
    severity character varying(10) NOT NULL,
    sim_time_seconds double precision NOT NULL,
    real_timestamp timestamp without time zone NOT NULL,
    robot_id integer,
    task_id integer,
    location_id character varying(50),
    route_id integer,
    message text NOT NULL,
    metadata text NOT NULL
);


ALTER TABLE public.simulation_events OWNER TO postgres;

--
-- Name: simulation_events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.simulation_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.simulation_events_id_seq OWNER TO postgres;

--
-- Name: simulation_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.simulation_events_id_seq OWNED BY public.simulation_events.id;


--
-- Name: simulation_snapshots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simulation_snapshots (
    id integer NOT NULL,
    simulation_id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    snapshot_version integer NOT NULL,
    taken_at timestamp without time zone NOT NULL,
    sim_time_seconds double precision NOT NULL,
    robot_states text NOT NULL,
    task_states text NOT NULL,
    obstacle_states text NOT NULL,
    sim_inventory_delta text NOT NULL,
    metadata text NOT NULL
);


ALTER TABLE public.simulation_snapshots OWNER TO postgres;

--
-- Name: simulation_snapshots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.simulation_snapshots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.simulation_snapshots_id_seq OWNER TO postgres;

--
-- Name: simulation_snapshots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.simulation_snapshots_id_seq OWNED BY public.simulation_snapshots.id;


--
-- Name: stock_movements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stock_movements (
    id integer NOT NULL,
    date date NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    item_id character varying(20) NOT NULL,
    stock_in integer,
    stock_out integer,
    closing_stock integer,
    is_anomaly boolean,
    anomaly_type character varying(30),
    entry_source character varying(20),
    entered_by character varying(64)
);


ALTER TABLE public.stock_movements OWNER TO postgres;

--
-- Name: stock_movements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stock_movements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stock_movements_id_seq OWNER TO postgres;

--
-- Name: stock_movements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stock_movements_id_seq OWNED BY public.stock_movements.id;


--
-- Name: system_health_snapshots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_health_snapshots (
    id integer NOT NULL,
    service character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    latency_ms double precision,
    "timestamp" timestamp without time zone NOT NULL
);


ALTER TABLE public.system_health_snapshots OWNER TO postgres;

--
-- Name: system_health_snapshots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.system_health_snapshots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.system_health_snapshots_id_seq OWNER TO postgres;

--
-- Name: system_health_snapshots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.system_health_snapshots_id_seq OWNED BY public.system_health_snapshots.id;


--
-- Name: system_incidents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_incidents (
    id integer NOT NULL,
    category character varying(50) NOT NULL,
    severity character varying(20) NOT NULL,
    title character varying(100) NOT NULL,
    description text NOT NULL,
    source character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    fingerprint character varying(128),
    started_at timestamp without time zone NOT NULL,
    resolved_at timestamp without time zone,
    acknowledged_by character varying(64),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.system_incidents OWNER TO postgres;

--
-- Name: system_incidents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.system_incidents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.system_incidents_id_seq OWNER TO postgres;

--
-- Name: system_incidents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.system_incidents_id_seq OWNED BY public.system_incidents.id;


--
-- Name: task_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_events (
    id integer NOT NULL,
    task_id integer NOT NULL,
    event_type character varying(50) NOT NULL,
    previous_status character varying(30),
    new_status character varying(30),
    user_id integer,
    created_at timestamp without time zone NOT NULL,
    reason text,
    metadata text NOT NULL
);


ALTER TABLE public.task_events OWNER TO postgres;

--
-- Name: task_events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.task_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.task_events_id_seq OWNER TO postgres;

--
-- Name: task_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.task_events_id_seq OWNED BY public.task_events.id;


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    task_number character varying(64) NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    task_type character varying(30) NOT NULL,
    priority character varying(20) NOT NULL,
    priority_score integer NOT NULL,
    status character varying(30) NOT NULL,
    source_type character varying(30),
    source_id character varying(64),
    order_id character varying(20),
    order_item_id integer,
    product_id character varying(20) NOT NULL,
    source_location_id character varying(50),
    destination_location_id character varying(50),
    requested_quantity integer NOT NULL,
    completed_quantity integer NOT NULL,
    assigned_user_id integer,
    assigned_robot_id character varying(50),
    created_at timestamp without time zone,
    prioritized_at timestamp without time zone,
    assigned_at timestamp without time zone,
    started_at timestamp without time zone,
    paused_at timestamp without time zone,
    completed_at timestamp without time zone,
    failed_at timestamp without time zone,
    cancelled_at timestamp without time zone,
    due_at timestamp without time zone,
    retry_count integer NOT NULL,
    failure_reason text,
    notes text,
    metadata text NOT NULL,
    depends_on_task_id integer
);


ALTER TABLE public.tasks OWNER TO postgres;

--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tasks_id_seq OWNER TO postgres;

--
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    session_token_hash character varying(64) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    last_seen_at timestamp without time zone,
    expires_at timestamp without time zone NOT NULL,
    revoked_at timestamp without time zone,
    revoke_reason character varying(100),
    login_method character varying(30),
    ip_address character varying(45),
    login_location character varying(255),
    user_agent character varying(500)
);


ALTER TABLE public.user_sessions OWNER TO postgres;

--
-- Name: user_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_sessions_id_seq OWNER TO postgres;

--
-- Name: user_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_sessions_id_seq OWNED BY public.user_sessions.id;


--
-- Name: user_warehouse_access; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_warehouse_access (
    id integer NOT NULL,
    user_id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.user_warehouse_access OWNER TO postgres;

--
-- Name: user_warehouse_access_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_warehouse_access_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_warehouse_access_id_seq OWNER TO postgres;

--
-- Name: user_warehouse_access_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_warehouse_access_id_seq OWNED BY public.user_warehouse_access.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(255),
    password_hash character varying(255) NOT NULL,
    role character varying(20) NOT NULL,
    full_name character varying(120),
    google_subject_id character varying(128),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    is_active boolean NOT NULL,
    is_verified boolean NOT NULL,
    last_login_at timestamp without time zone,
    last_logout_at timestamp without time zone,
    last_login_ip character varying(45),
    login_location character varying(255),
    login_method character varying(30),
    failed_login_count integer NOT NULL,
    locked_until timestamp without time zone,
    email_verified_at timestamp without time zone,
    password_changed_at timestamp without time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: warehouse_grid_cells; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.warehouse_grid_cells (
    id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    x integer NOT NULL,
    y integer NOT NULL,
    cell_type character varying(30) NOT NULL,
    traversable boolean NOT NULL,
    occupied boolean NOT NULL,
    restricted boolean NOT NULL,
    cost double precision NOT NULL,
    metadata text NOT NULL
);


ALTER TABLE public.warehouse_grid_cells OWNER TO postgres;

--
-- Name: warehouse_grid_cells_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.warehouse_grid_cells_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.warehouse_grid_cells_id_seq OWNER TO postgres;

--
-- Name: warehouse_grid_cells_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.warehouse_grid_cells_id_seq OWNED BY public.warehouse_grid_cells.id;


--
-- Name: warehouse_locations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.warehouse_locations (
    id character varying(50) NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    zone character varying(20) NOT NULL,
    aisle character varying(20) NOT NULL,
    rack character varying(20) NOT NULL,
    shelf character varying(20) NOT NULL,
    x double precision,
    y double precision,
    capacity integer,
    current_utilization integer,
    location_type character varying(20),
    status character varying(20),
    created_at timestamp without time zone
);


ALTER TABLE public.warehouse_locations OWNER TO postgres;

--
-- Name: warehouse_obstacles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.warehouse_obstacles (
    id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    obstacle_type character varying(30) NOT NULL,
    x integer NOT NULL,
    y integer NOT NULL,
    width integer NOT NULL,
    height integer NOT NULL,
    active boolean NOT NULL,
    severity character varying(20) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.warehouse_obstacles OWNER TO postgres;

--
-- Name: warehouse_obstacles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.warehouse_obstacles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.warehouse_obstacles_id_seq OWNER TO postgres;

--
-- Name: warehouse_obstacles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.warehouse_obstacles_id_seq OWNED BY public.warehouse_obstacles.id;


--
-- Name: warehouses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.warehouses (
    id character varying(20) NOT NULL,
    name character varying(120) NOT NULL,
    location character varying(120),
    latitude double precision,
    longitude double precision,
    created_at timestamp without time zone
);


ALTER TABLE public.warehouses OWNER TO postgres;

--
-- Name: access_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.access_log ALTER COLUMN id SET DEFAULT nextval('public.access_log_id_seq'::regclass);


--
-- Name: ai_recommendations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_recommendations ALTER COLUMN id SET DEFAULT nextval('public.ai_recommendations_id_seq'::regclass);


--
-- Name: audit_ledger id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_ledger ALTER COLUMN id SET DEFAULT nextval('public.audit_ledger_id_seq'::regclass);


--
-- Name: backup_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backup_records ALTER COLUMN id SET DEFAULT nextval('public.backup_records_id_seq'::regclass);


--
-- Name: digital_twin_simulations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.digital_twin_simulations ALTER COLUMN id SET DEFAULT nextval('public.digital_twin_simulations_id_seq'::regclass);


--
-- Name: experiment_runs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_runs ALTER COLUMN id SET DEFAULT nextval('public.experiment_runs_id_seq'::regclass);


--
-- Name: experiments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiments ALTER COLUMN id SET DEFAULT nextval('public.experiments_id_seq'::regclass);


--
-- Name: health_thresholds id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.health_thresholds ALTER COLUMN id SET DEFAULT nextval('public.health_thresholds_id_seq'::regclass);


--
-- Name: inventory id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory ALTER COLUMN id SET DEFAULT nextval('public.inventory_id_seq'::regclass);


--
-- Name: inventory_reservations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_reservations ALTER COLUMN id SET DEFAULT nextval('public.inventory_reservations_id_seq'::regclass);


--
-- Name: notification_preferences id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_preferences ALTER COLUMN id SET DEFAULT nextval('public.notification_preferences_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: order_events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_events ALTER COLUMN id SET DEFAULT nextval('public.order_events_id_seq'::regclass);


--
-- Name: order_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items ALTER COLUMN id SET DEFAULT nextval('public.order_items_id_seq'::regclass);


--
-- Name: otp_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otp_records ALTER COLUMN id SET DEFAULT nextval('public.otp_records_id_seq'::regclass);


--
-- Name: packing_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.packing_records ALTER COLUMN id SET DEFAULT nextval('public.packing_records_id_seq'::regclass);


--
-- Name: recovery_codes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recovery_codes ALTER COLUMN id SET DEFAULT nextval('public.recovery_codes_id_seq'::regclass);


--
-- Name: recovery_credentials id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recovery_credentials ALTER COLUMN id SET DEFAULT nextval('public.recovery_credentials_id_seq'::regclass);


--
-- Name: robot_reservations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_reservations ALTER COLUMN id SET DEFAULT nextval('public.robot_reservations_id_seq'::regclass);


--
-- Name: robot_routes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_routes ALTER COLUMN id SET DEFAULT nextval('public.robot_routes_id_seq'::regclass);


--
-- Name: robot_telemetry id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_telemetry ALTER COLUMN id SET DEFAULT nextval('public.robot_telemetry_id_seq'::regclass);


--
-- Name: robots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robots ALTER COLUMN id SET DEFAULT nextval('public.robots_id_seq'::regclass);


--
-- Name: scenarios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scenarios ALTER COLUMN id SET DEFAULT nextval('public.scenarios_id_seq'::regclass);


--
-- Name: shrinkage_flags id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shrinkage_flags ALTER COLUMN id SET DEFAULT nextval('public.shrinkage_flags_id_seq'::regclass);


--
-- Name: simulation_events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_events ALTER COLUMN id SET DEFAULT nextval('public.simulation_events_id_seq'::regclass);


--
-- Name: simulation_snapshots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_snapshots ALTER COLUMN id SET DEFAULT nextval('public.simulation_snapshots_id_seq'::regclass);


--
-- Name: stock_movements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements ALTER COLUMN id SET DEFAULT nextval('public.stock_movements_id_seq'::regclass);


--
-- Name: system_health_snapshots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_health_snapshots ALTER COLUMN id SET DEFAULT nextval('public.system_health_snapshots_id_seq'::regclass);


--
-- Name: system_incidents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_incidents ALTER COLUMN id SET DEFAULT nextval('public.system_incidents_id_seq'::regclass);


--
-- Name: task_events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_events ALTER COLUMN id SET DEFAULT nextval('public.task_events_id_seq'::regclass);


--
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- Name: user_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions ALTER COLUMN id SET DEFAULT nextval('public.user_sessions_id_seq'::regclass);


--
-- Name: user_warehouse_access id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_warehouse_access ALTER COLUMN id SET DEFAULT nextval('public.user_warehouse_access_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: warehouse_grid_cells id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_grid_cells ALTER COLUMN id SET DEFAULT nextval('public.warehouse_grid_cells_id_seq'::regclass);


--
-- Name: warehouse_obstacles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_obstacles ALTER COLUMN id SET DEFAULT nextval('public.warehouse_obstacles_id_seq'::regclass);


--
-- Data for Name: access_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.access_log (id, "timestamp", username, warehouse_id, action, ip_address) FROM stdin;
533	2026-08-19 18:24:17.898041	test_admin_hardened		login	testclient
\.


--
-- Data for Name: ai_recommendations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ai_recommendations (id, "timestamp", warehouse_id, item_id, title, risk_level, action_recommended, confidence_score, input_factors, status, decision_by, decision_time, notes, recommendation_type, description, priority, score, confidence_or_reliability, source_model, source_entity_type, source_entity_id, recommended_action, estimated_impact, explanation, supporting_metrics, created_at, reviewed_at, reviewed_by, review_notes, expires_at, metadata) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
c6a0f47c242e
\.


--
-- Data for Name: audit_ledger; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_ledger (id, "timestamp", event_type, details, prev_hash, hash) FROM stdin;
728	2026-08-19 18:24:17	user_login	{"username": "test_admin_hardened", "role": "admin", "method": "password", "ip": "testclient", "time": "2026-08-19T18:24:17.913292"}	0000000000000000000000000000000000000000000000000000000000000000	2d0eb7e365fe6534313bc3100d32fb18918d75339f53cf05b55e774803c8ff60
729	2026-08-19 18:24:17	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "5", "source_entity_type": "USER", "recipients_count": 3}	2d0eb7e365fe6534313bc3100d32fb18918d75339f53cf05b55e774803c8ff60	862640f5c9895f6a9b011cfdc7763dc7b7af8cdab8a9d8336fcada08d36b1c8e
\.


--
-- Data for Name: backup_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.backup_records (id, backup_id, filename, created_at, size_bytes, sha256, status, storage_key, error_message, backup_type, started_at, completed_at, storage_provider, bucket, checksum_algorithm, verification_status, verification_at, restore_test_status, restore_test_at, retention_status, initiated_by, audit_ref) FROM stdin;
13	BK-7C5FE0477FA99D5D	warehouse_postgres_2026-08-19_18-24-17.sql.gz	2026-08-19 18:24:17.956875	\N	\N	RUNNING	\N	\N	MANUAL	2026-08-19 18:24:17.956875	\N	Backblaze B2 Storage	harsha-warehouse-backups	SHA-256	PENDING	\N	PENDING	\N	ACTIVE	SYSTEM	\N
\.


--
-- Data for Name: digital_twin_simulations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.digital_twin_simulations (id, warehouse_id, simulation_status, simulation_time_seconds, speed_multiplier, seed, mode, scenario_type, tick_count, created_at, started_at, paused_at, stopped_at, completed_at, error_message, created_by) FROM stdin;
\.


--
-- Data for Name: experiment_runs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.experiment_runs (id, experiment_id, repetition_number, random_seed, status, started_at, completed_at, duration_seconds, error_message, metrics, created_at) FROM stdin;
\.


--
-- Data for Name: experiments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.experiments (id, scenario_id, experiment_name, description, status, algorithm_name, algorithm_version, configuration, random_seed, repetitions, started_at, completed_at, duration_seconds, created_by, error_message, metrics_summary, created_at) FROM stdin;
\.


--
-- Data for Name: health_thresholds; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.health_thresholds (id, key, value, description, created_at, updated_at) FROM stdin;
13	api_latency_warning_ms	400	Warn	2026-08-19 18:22:50.801112	2026-08-19 18:22:50.833288
14	queue_warning_depth	10	Warning threshold for RabbitMQ queue depth	2026-08-19 18:24:12.94791	2026-08-19 18:24:12.94791
15	queue_critical_depth	50	Critical threshold for RabbitMQ queue depth	2026-08-19 18:24:12.94791	2026-08-19 18:24:12.94791
16	api_latency_critical_ms	1000	Critical threshold for API request response time	2026-08-19 18:24:12.94791	2026-08-19 18:24:12.94791
17	database_latency_warning_ms	100	Warning threshold for Supabase DB response time	2026-08-19 18:24:12.94791	2026-08-19 18:24:12.94791
18	database_latency_critical_ms	500	Critical threshold for Supabase DB response time	2026-08-19 18:24:12.94791	2026-08-19 18:24:12.94791
19	backup_age_warning_hours	26	Warning threshold for backup age	2026-08-19 18:24:12.94791	2026-08-19 18:24:12.94791
20	backup_age_critical_hours	48	Critical threshold for backup age	2026-08-19 18:24:12.94791	2026-08-19 18:24:12.94791
21	worker_stale_timeout_seconds	60	Heartbeat threshold for stale Celery worker status	2026-08-19 18:24:12.94791	2026-08-19 18:24:12.94791
22	api_error_rate_warning_pct	5	Warning threshold for API request error percentage	2026-08-19 18:24:12.94791	2026-08-19 18:24:12.94791
23	api_error_rate_critical_pct	15	Critical threshold for API request error percentage	2026-08-19 18:24:12.94791	2026-08-19 18:24:12.94791
\.


--
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inventory (id, warehouse_id, item_id, location_id, on_hand, reserved, available, damaged, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: inventory_reservations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inventory_reservations (id, order_id, item_id, location_id, reserved_qty, released_qty, created_at) FROM stdin;
\.


--
-- Data for Name: items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.items (id, name, category, unit_cost, lead_time_days, safety_stock, sku, description, unit, weight_kg, dimensions, barcode, is_active, reorder_threshold, preferred_storage_type, created_at) FROM stdin;
ITM-CPU-01	AMD Ryzen 9 7900X Processor	Electronics	38000	5	15	\N	\N	units	0		\N	t	20	STORAGE	2026-08-19 18:23:32.856645
ITM-GPU-01	Nvidia RTX 4080 Founders Edition	Electronics	95000	7	10	\N	\N	units	0		\N	t	20	STORAGE	2026-08-19 18:23:32.862654
ITM-RAM-01	Corsair DDR5 32GB 6000MHz RAM	Electronics	8500	4	25	\N	\N	units	0		\N	t	20	STORAGE	2026-08-19 18:23:32.866822
ITM-SSD-01	Samsung 990 Pro 2TB NVMe SSD	Storage	12000	3	30	\N	\N	units	0		\N	t	20	STORAGE	2026-08-19 18:23:32.87293
ITM-HDD-01	WD Red Pro 8TB NAS Hard Drive	Storage	16500	5	20	\N	\N	units	0		\N	t	20	STORAGE	2026-08-19 18:23:32.876925
ITM-CHG-01	Anker 100W GaN Wall Charger	Accessories	2500	2	50	\N	\N	units	0		\N	t	20	STORAGE	2026-08-19 18:23:32.882464
ITM-CBL-01	Apple USB-C Braided Cable 2m	Accessories	800	1	100	\N	\N	units	0		\N	t	20	STORAGE	2026-08-19 18:23:32.887449
\.


--
-- Data for Name: notification_preferences; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notification_preferences (id, user_id, category, in_app_enabled, email_enabled, min_severity, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notifications (id, user_id, warehouse_id, event_type, notification_type, title, message, severity, status, channel, source_entity_type, source_entity_id, created_at, read_at, delivered_at, failed_at, retry_count, expires_at, metadata, idempotency_key) FROM stdin;
141	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_admin_hardened logged in successfully.	INFO	DELIVERED	IN_APP	USER	5	2026-08-19 18:22:23.132525	\N	2026-08-19 18:22:23.194265	\N	0	\N	{"username": "test_admin_hardened", "message": "User test_admin_hardened logged in successfully."}	USER_LOGIN_5_2_1787143943.132525
147	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_e2e_admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	18	2026-08-19 18:22:41.486292	\N	2026-08-19 18:22:41.509601	\N	0	\N	{"username": "test_e2e_admin", "message": "User test_e2e_admin logged in successfully."}	USER_LOGIN_18_1_1787143961.486292
166	3	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-B	2026-08-19 18:22:43.591168	\N	2026-08-19 18:22:43.613389	\N	0	\N	{"robot_code": "ROB-B", "task_number": "TSK-E2E-PICK-2", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-B_3_1787143963.591168
168	1	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-B	2026-08-19 18:22:43.591168	\N	2026-08-19 18:22:43.632057	\N	0	\N	{"robot_code": "ROB-B", "task_number": "TSK-E2E-PICK-2", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-B_1_1787143963.591168
172	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_path_admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	19	2026-08-19 18:22:45.518053	\N	2026-08-19 18:22:45.537124	\N	0	\N	{"username": "test_path_admin", "message": "User test_path_admin logged in successfully."}	USER_LOGIN_19_5_1787143965.518053
175	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_path_admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	19	2026-08-19 18:22:45.518053	\N	2026-08-19 18:22:45.557397	\N	0	\N	{"username": "test_path_admin", "message": "User test_path_admin logged in successfully."}	USER_LOGIN_19_1_1787143965.518053
195	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_tasks_staff logged in successfully.	INFO	DELIVERED	IN_APP	USER	20	2026-08-19 18:22:52.736706	\N	2026-08-19 18:22:52.753701	\N	0	\N	{"username": "test_tasks_staff", "message": "User test_tasks_staff logged in successfully."}	USER_LOGIN_20_5_1787143972.736706
199	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_tasks_staff logged in successfully.	INFO	DELIVERED	IN_APP	USER	20	2026-08-19 18:22:52.736706	\N	2026-08-19 18:22:52.7747	\N	0	\N	{"username": "test_tasks_staff", "message": "User test_tasks_staff logged in successfully."}	USER_LOGIN_20_2_1787143972.736706
139	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_admin_hardened logged in successfully.	INFO	DELIVERED	IN_APP	USER	5	2026-08-19 18:22:23.132525	\N	2026-08-19 18:22:23.168695	\N	0	\N	{"username": "test_admin_hardened", "message": "User test_admin_hardened logged in successfully."}	USER_LOGIN_5_5_1787143943.132525
148	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_e2e_admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	18	2026-08-19 18:22:41.486292	\N	2026-08-19 18:22:41.516673	\N	0	\N	{"username": "test_e2e_admin", "message": "User test_e2e_admin logged in successfully."}	USER_LOGIN_18_2_1787143961.486292
176	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_path_admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	19	2026-08-19 18:22:45.518053	\N	2026-08-19 18:22:45.56225	\N	0	\N	{"username": "test_path_admin", "message": "User test_path_admin logged in successfully."}	USER_LOGIN_19_2_1787143965.518053
180	3	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-PATH-E2E	2026-08-19 18:22:46.011086	\N	2026-08-19 18:22:46.038906	\N	0	\N	{"robot_code": "ROB-PATH-E2E", "task_number": "TSK-PATH-01", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-PATH-E2E_3_1787143966.011086
184	2	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-PATH-E2E	2026-08-19 18:22:46.011086	\N	2026-08-19 18:22:46.063524	\N	0	\N	{"robot_code": "ROB-PATH-E2E", "task_number": "TSK-PATH-01", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-PATH-E2E_2_1787143966.011086
198	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_tasks_staff logged in successfully.	INFO	DELIVERED	IN_APP	USER	20	2026-08-19 18:22:52.736706	\N	2026-08-19 18:22:52.769697	\N	0	\N	{"username": "test_tasks_staff", "message": "User test_tasks_staff logged in successfully."}	USER_LOGIN_20_1_1787143972.736706
140	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_admin_hardened logged in successfully.	INFO	DELIVERED	IN_APP	USER	5	2026-08-19 18:22:23.132525	\N	2026-08-19 18:22:23.184721	\N	0	\N	{"username": "test_admin_hardened", "message": "User test_admin_hardened logged in successfully."}	USER_LOGIN_5_1_1787143943.132525
145	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_e2e_admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	18	2026-08-19 18:22:41.486292	\N	2026-08-19 18:22:41.497602	\N	0	\N	{"username": "test_e2e_admin", "message": "User test_e2e_admin logged in successfully."}	USER_LOGIN_18_5_1787143961.486292
154	1	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-E2E-01	2026-08-19 18:22:41.994485	\N	2026-08-19 18:22:42.022203	\N	0	\N	{"robot_code": "ROB-E2E-01", "task_number": "TSK-E2E-PICK-1", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-E2E-01_1_1787143961.994485
158	5	\N	ROBOT_FAILED	ROBOTS_ALERT	Robot Failed Alert	Robot ROB-A failed in None. Action is required.	HIGH	DELIVERED	IN_APP	ROBOT	ROB-A	2026-08-19 18:22:43.216721	\N	2026-08-19 18:22:43.230938	\N	0	\N	{"robot_code": "ROB-A", "failure_count": 1, "message": "Robot ROB-A failed in None. Action is required."}	ROBOT_FAILED_ROB-A_5_1787143963.216721
162	2	\N	ROBOT_FAILED	ROBOTS_ALERT	Robot Failed Alert	Robot ROB-A failed in None. Action is required.	HIGH	DELIVERED	IN_APP	ROBOT	ROB-A	2026-08-19 18:22:43.216721	\N	2026-08-19 18:22:43.252288	\N	0	\N	{"robot_code": "ROB-A", "failure_count": 1, "message": "Robot ROB-A failed in None. Action is required."}	ROBOT_FAILED_ROB-A_2_1787143963.216721
165	5	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-B	2026-08-19 18:22:43.591168	\N	2026-08-19 18:22:43.607409	\N	0	\N	{"robot_code": "ROB-B", "task_number": "TSK-E2E-PICK-2", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-B_5_1787143963.591168
169	2	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-B	2026-08-19 18:22:43.591168	\N	2026-08-19 18:22:43.641588	\N	0	\N	{"robot_code": "ROB-B", "task_number": "TSK-E2E-PICK-2", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-B_2_1787143963.591168
187	5	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-REPLAN	2026-08-19 18:22:47.394982	\N	2026-08-19 18:22:47.408993	\N	0	\N	{"robot_code": "ROB-REPLAN", "task_number": "TSK-PATH-03", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-REPLAN_5_1787143967.394982
191	1	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-REPLAN	2026-08-19 18:22:47.394982	\N	2026-08-19 18:22:47.427744	\N	0	\N	{"robot_code": "ROB-REPLAN", "task_number": "TSK-PATH-03", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-REPLAN_1_1787143967.394982
151	5	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-E2E-01	2026-08-19 18:22:41.994485	\N	2026-08-19 18:22:42.007207	\N	0	\N	{"robot_code": "ROB-E2E-01", "task_number": "TSK-E2E-PICK-1", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-E2E-01_5_1787143961.994485
153	3	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-E2E-01	2026-08-19 18:22:41.994485	\N	2026-08-19 18:22:42.016967	\N	0	\N	{"robot_code": "ROB-E2E-01", "task_number": "TSK-E2E-PICK-1", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-E2E-01_3_1787143961.994485
155	2	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-E2E-01	2026-08-19 18:22:41.994485	\N	2026-08-19 18:22:42.026501	\N	0	\N	{"robot_code": "ROB-E2E-01", "task_number": "TSK-E2E-PICK-1", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-E2E-01_2_1787143961.994485
159	3	\N	ROBOT_FAILED	ROBOTS_ALERT	Robot Failed Alert	Robot ROB-A failed in None. Action is required.	HIGH	DELIVERED	IN_APP	ROBOT	ROB-A	2026-08-19 18:22:43.216721	\N	2026-08-19 18:22:43.235665	\N	0	\N	{"robot_code": "ROB-A", "failure_count": 1, "message": "Robot ROB-A failed in None. Action is required."}	ROBOT_FAILED_ROB-A_3_1787143963.216721
161	1	\N	ROBOT_FAILED	ROBOTS_ALERT	Robot Failed Alert	Robot ROB-A failed in None. Action is required.	HIGH	DELIVERED	IN_APP	ROBOT	ROB-A	2026-08-19 18:22:43.216721	\N	2026-08-19 18:22:43.247576	\N	0	\N	{"robot_code": "ROB-A", "failure_count": 1, "message": "Robot ROB-A failed in None. Action is required."}	ROBOT_FAILED_ROB-A_1_1787143963.216721
179	5	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-PATH-E2E	2026-08-19 18:22:46.011086	\N	2026-08-19 18:22:46.030768	\N	0	\N	{"robot_code": "ROB-PATH-E2E", "task_number": "TSK-PATH-01", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-PATH-E2E_5_1787143966.011086
183	1	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-PATH-E2E	2026-08-19 18:22:46.011086	\N	2026-08-19 18:22:46.054093	\N	0	\N	{"robot_code": "ROB-PATH-E2E", "task_number": "TSK-PATH-01", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-PATH-E2E_1_1787143966.011086
188	3	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-REPLAN	2026-08-19 18:22:47.394982	\N	2026-08-19 18:22:47.412984	\N	0	\N	{"robot_code": "ROB-REPLAN", "task_number": "TSK-PATH-03", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-REPLAN_3_1787143967.394982
192	2	\N	TASK_COMPLETED	TASKS_ALERT	Task Completed Alert	System event 'ROBOT_TASK_COMPLETED' processed successfully.	SUCCESS	DELIVERED	IN_APP	ROBOT	ROB-REPLAN	2026-08-19 18:22:47.394982	\N	2026-08-19 18:22:47.432351	\N	0	\N	{"robot_code": "ROB-REPLAN", "task_number": "TSK-PATH-03", "message": "System event 'ROBOT_TASK_COMPLETED' processed successfully."}	TASK_COMPLETED_ROB-REPLAN_2_1787143967.394982
115	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User notif_admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	15	2026-08-19 18:21:33.938399	\N	2026-08-19 18:21:33.94487	\N	0	\N	{"username": "notif_admin", "message": "User notif_admin logged in successfully."}	USER_LOGIN_15_1_1787143893.938399
116	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User notif_admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	15	2026-08-19 18:21:33.938399	\N	2026-08-19 18:21:33.949884	\N	0	\N	{"username": "notif_admin", "message": "User notif_admin logged in successfully."}	USER_LOGIN_15_5_1787143893.938399
117	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User notif_admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	15	2026-08-19 18:21:33.938399	\N	2026-08-19 18:21:33.956873	\N	0	\N	{"username": "notif_admin", "message": "User notif_admin logged in successfully."}	USER_LOGIN_15_2_1787143893.938399
121	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_staff logged in successfully.	INFO	DELIVERED	IN_APP	USER	16	2026-08-19 18:21:38.804724	\N	2026-08-19 18:21:38.81972	\N	0	\N	{"username": "test_staff", "message": "User test_staff logged in successfully."}	USER_LOGIN_16_5_1787143898.804724
122	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_staff logged in successfully.	INFO	DELIVERED	IN_APP	USER	16	2026-08-19 18:21:38.804724	\N	2026-08-19 18:21:38.827721	\N	0	\N	{"username": "test_staff", "message": "User test_staff logged in successfully."}	USER_LOGIN_16_2_1787143898.804724
126	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_robots_admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	17	2026-08-19 18:21:52.638552	\N	2026-08-19 18:21:52.654364	\N	0	\N	{"username": "test_robots_admin", "message": "User test_robots_admin logged in successfully."}	USER_LOGIN_17_1_1787143912.638552
127	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_robots_admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	17	2026-08-19 18:21:52.638552	\N	2026-08-19 18:21:52.661628	\N	0	\N	{"username": "test_robots_admin", "message": "User test_robots_admin logged in successfully."}	USER_LOGIN_17_5_1787143912.638552
128	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_robots_admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	17	2026-08-19 18:21:52.638552	\N	2026-08-19 18:21:52.667633	\N	0	\N	{"username": "test_robots_admin", "message": "User test_robots_admin logged in successfully."}	USER_LOGIN_17_2_1787143912.638552
132	3	\N	ROBOT_FAILED	ROBOTS_ALERT	Robot Failed Alert	Robot ROB-FAIL failed in None. Action is required.	HIGH	DELIVERED	IN_APP	ROBOT	ROB-FAIL	2026-08-19 18:22:01.987214	\N	2026-08-19 18:22:02.002309	\N	0	\N	{"robot_code": "ROB-FAIL", "failure_count": 1, "message": "Robot ROB-FAIL failed in None. Action is required."}	ROBOT_FAILED_ROB-FAIL_3_1787143921.987214
133	1	\N	ROBOT_FAILED	ROBOTS_ALERT	Robot Failed Alert	Robot ROB-FAIL failed in None. Action is required.	HIGH	DELIVERED	IN_APP	ROBOT	ROB-FAIL	2026-08-19 18:22:01.987214	\N	2026-08-19 18:22:02.010008	\N	0	\N	{"robot_code": "ROB-FAIL", "failure_count": 1, "message": "Robot ROB-FAIL failed in None. Action is required."}	ROBOT_FAILED_ROB-FAIL_1_1787143921.987214
134	5	\N	ROBOT_FAILED	ROBOTS_ALERT	Robot Failed Alert	Robot ROB-FAIL failed in None. Action is required.	HIGH	DELIVERED	IN_APP	ROBOT	ROB-FAIL	2026-08-19 18:22:01.987214	\N	2026-08-19 18:22:02.017689	\N	0	\N	{"robot_code": "ROB-FAIL", "failure_count": 1, "message": "Robot ROB-FAIL failed in None. Action is required."}	ROBOT_FAILED_ROB-FAIL_5_1787143921.987214
135	2	\N	ROBOT_FAILED	ROBOTS_ALERT	Robot Failed Alert	Robot ROB-FAIL failed in None. Action is required.	HIGH	DELIVERED	IN_APP	ROBOT	ROB-FAIL	2026-08-19 18:22:01.987214	\N	2026-08-19 18:22:02.023493	\N	0	\N	{"robot_code": "ROB-FAIL", "failure_count": 1, "message": "Robot ROB-FAIL failed in None. Action is required."}	ROBOT_FAILED_ROB-FAIL_2_1787143921.987214
120	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_staff logged in successfully.	INFO	DELIVERED	IN_APP	USER	16	2026-08-19 18:21:38.804724	\N	2026-08-19 18:21:38.813734	\N	0	\N	{"username": "test_staff", "message": "User test_staff logged in successfully."}	USER_LOGIN_16_1_1787143898.804724
\.


--
-- Data for Name: order_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_events (id, order_id, "timestamp", status, event_type, operator, notes) FROM stdin;
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_items (id, order_id, item_id, requested_qty, reserved_qty, picked_qty, packed_qty, shipped_qty, status) FROM stdin;
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (id, customer_ref, warehouse_id, created_at, updated_at, status, priority, total_items, notes, created_by) FROM stdin;
\.


--
-- Data for Name: otp_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.otp_records (id, user_id, purpose, code_hash, expires_at, attempts, max_attempts, consumed_at, created_at, request_ip, context_data) FROM stdin;
1	1	ADMIN_CREATION	$2b$12$3xqRDMhLeoAerRIDkUlr5OzzABgRkrLPjfZCKGTPj3edBn/wUBsui	2026-08-19 17:04:52.461116	2	5	2026-08-19 16:55:59.972851	2026-08-19 16:54:52.461116	127.0.0.1	{"target_email": "harsha200797@gmail.com", "full_name": "harshavardhan", "target_role": "admin"}
2	2	PASSWORD_CHANGE	$2b$12$JxlKold6nS4f1Zi8DhtUl.JbN8T.p4wLdwsYv4oAFLlQR9i0tyG2W	2026-08-19 18:30:09.582648	2	5	2026-08-19 18:20:15.708313	2026-08-19 18:20:09.582648	testclient	{"new_password_hash": "$2b$12$6r11Vxdfp6ZAFSeRFIDIqezssLxtfn8KMuApYPmwW6UwYWNlrOZYO"}
4	5	ADMIN_CREATION	$2b$12$xKzg8JY59zwC24P3qe0PbeL2.stlUZYXh2u4rkIYG8TMmVUFrC/Oa	2026-08-19 18:32:29.709933	1	5	\N	2026-08-19 18:22:29.709933	testclient	{"target_email": "testadmin.security@gmail.com", "full_name": "Test Security Admin", "target_role": "admin"}
\.


--
-- Data for Name: packing_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.packing_records (id, order_id, status, started_at, completed_at, operator, package_count, weight_kg, notes) FROM stdin;
\.


--
-- Data for Name: recovery_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.recovery_codes (id, user_id, code_hash, used, created_at, used_at) FROM stdin;
\.


--
-- Data for Name: recovery_credentials; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.recovery_credentials (id, user_id, password_hash, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: robot_reservations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.robot_reservations (id, robot_id, warehouse_id, x, y, tick) FROM stdin;
\.


--
-- Data for Name: robot_routes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.robot_routes (id, robot_id, task_id, warehouse_id, start_x, start_y, goal_x, goal_y, algorithm, path_data, distance, cost, status, created_at, completed_at) FROM stdin;
\.


--
-- Data for Name: robot_telemetry; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.robot_telemetry (id, robot_id, event_type, "timestamp", x, y, battery, status, task_id, metadata) FROM stdin;
\.


--
-- Data for Name: robots; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.robots (id, robot_code, name, warehouse_id, status, battery_level, current_location_id, current_x, current_y, target_location_id, target_x, target_y, assigned_task_id, total_tasks_completed, total_distance, total_operating_time, utilization_percent, failure_count, created_at, updated_at, last_heartbeat_at, robot_type, max_payload, max_speed, enabled, metadata) FROM stdin;
80	RB-BLR-03	Bangalore AGV 03	WH-BLR-01	IDLE	92.5	\N	1	5	\N	0	0	\N	0	0	0	0	0	2026-08-19 18:23:33.250656	2026-08-19 18:23:33.250656	2026-08-19 18:23:33.250656	AGV	200	1.5	t	{}
78	RB-BLR-01	Bangalore AGV 01	WH-BLR-01	CHARGING	100	\N	11	5	\N	0	0	\N	0	0	0	0	0	2026-08-19 18:23:33.250656	2026-08-19 18:23:33.250656	2026-08-19 18:23:33.250656	AGV	200	1.5	t	{}
79	RB-BLR-02	Bangalore AGV 02	WH-BLR-01	CHARGING	100	\N	12	5	\N	0	0	\N	0	0	0	0	0	2026-08-19 18:23:33.250656	2026-08-19 18:23:33.250656	2026-08-19 18:23:33.250656	AGV	200	1.5	t	{}
81	RB-CHN-01	Chennai AGV 01	WH-CHN-01	CHARGING	100	\N	11	5	\N	0	0	\N	0	0	0	0	0	2026-08-19 18:23:33.250656	2026-08-19 18:23:33.250656	2026-08-19 18:23:33.250656	AGV	200	1.5	t	{}
82	RB-BOM-01	Mumbai AGV 01	WH-BOM-01	CHARGING	100	\N	11	5	\N	0	0	\N	0	0	0	0	0	2026-08-19 18:23:33.250656	2026-08-19 18:23:33.250656	2026-08-19 18:23:33.250656	AGV	200	1.5	t	{}
83	RB-DEL-01	Delhi AGV 01	WH-DEL-01	CHARGING	100	\N	11	5	\N	0	0	\N	0	0	0	0	0	2026-08-19 18:23:33.250656	2026-08-19 18:23:33.250656	2026-08-19 18:23:33.250656	AGV	200	1.5	t	{}
84	RB-CCU-01	Kolkata AGV 01	WH-CCU-01	CHARGING	100	\N	11	5	\N	0	0	\N	0	0	0	0	0	2026-08-19 18:23:33.250656	2026-08-19 18:23:33.250656	2026-08-19 18:23:33.250656	AGV	200	1.5	t	{}
\.


--
-- Data for Name: scenarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.scenarios (id, name, description, warehouse_id, scenario_type, configuration, random_seed, status, tags, notes, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: shipments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.shipments (id, order_id, status, tracking_reference, carrier, created_at, shipped_at, delivered_at) FROM stdin;
\.


--
-- Data for Name: shrinkage_flags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.shrinkage_flags (id, date, warehouse_id, item_id, item_name, deviation_score, expected_quantity, actual_quantity, discrepancy_quantity, estimated_exposure, severity, likely_cause, explanation) FROM stdin;
\.


--
-- Data for Name: simulation_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.simulation_events (id, simulation_id, warehouse_id, event_type, severity, sim_time_seconds, real_timestamp, robot_id, task_id, location_id, route_id, message, metadata) FROM stdin;
\.


--
-- Data for Name: simulation_snapshots; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.simulation_snapshots (id, simulation_id, warehouse_id, snapshot_version, taken_at, sim_time_seconds, robot_states, task_states, obstacle_states, sim_inventory_delta, metadata) FROM stdin;
\.


--
-- Data for Name: stock_movements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.stock_movements (id, date, warehouse_id, item_id, stock_in, stock_out, closing_stock, is_anomaly, anomaly_type, entry_source, entered_by) FROM stdin;
8591	2026-07-13	WH-BLR-01	ITM-CPU-01	0	3	42	f	none	simulated	system_sim
8592	2026-07-13	WH-BLR-01	ITM-GPU-01	0	0	30	f	none	simulated	system_sim
8593	2026-07-13	WH-BLR-01	ITM-RAM-01	0	1	74	f	none	simulated	system_sim
8594	2026-07-13	WH-BLR-01	ITM-SSD-01	0	2	88	f	none	simulated	system_sim
8595	2026-07-13	WH-BLR-01	ITM-HDD-01	0	0	60	f	none	simulated	system_sim
8596	2026-07-13	WH-BLR-01	ITM-CHG-01	0	10	140	f	none	simulated	system_sim
8597	2026-07-13	WH-BLR-01	ITM-CBL-01	0	8	292	f	none	simulated	system_sim
8598	2026-07-13	WH-CHN-01	ITM-CPU-01	0	2	43	f	none	simulated	system_sim
8599	2026-07-13	WH-CHN-01	ITM-GPU-01	0	0	30	f	none	simulated	system_sim
8600	2026-07-13	WH-CHN-01	ITM-RAM-01	0	2	73	f	none	simulated	system_sim
8601	2026-07-13	WH-CHN-01	ITM-SSD-01	0	0	90	f	none	simulated	system_sim
8602	2026-07-13	WH-CHN-01	ITM-HDD-01	0	1	59	f	none	simulated	system_sim
8603	2026-07-13	WH-CHN-01	ITM-CHG-01	0	6	144	f	none	simulated	system_sim
8604	2026-07-13	WH-CHN-01	ITM-CBL-01	0	8	292	f	none	simulated	system_sim
8605	2026-07-13	WH-BOM-01	ITM-CPU-01	0	1	44	f	none	simulated	system_sim
8606	2026-07-13	WH-BOM-01	ITM-GPU-01	0	2	28	f	none	simulated	system_sim
8607	2026-07-13	WH-BOM-01	ITM-RAM-01	0	5	70	f	none	simulated	system_sim
8608	2026-07-13	WH-BOM-01	ITM-SSD-01	0	2	88	f	none	simulated	system_sim
8609	2026-07-13	WH-BOM-01	ITM-HDD-01	0	1	59	f	none	simulated	system_sim
8610	2026-07-13	WH-BOM-01	ITM-CHG-01	0	3	147	f	none	simulated	system_sim
8611	2026-07-13	WH-BOM-01	ITM-CBL-01	0	1	299	f	none	simulated	system_sim
8612	2026-07-13	WH-DEL-01	ITM-CPU-01	0	2	43	f	none	simulated	system_sim
8613	2026-07-13	WH-DEL-01	ITM-GPU-01	0	0	30	f	none	simulated	system_sim
8614	2026-07-13	WH-DEL-01	ITM-RAM-01	0	1	74	f	none	simulated	system_sim
8615	2026-07-13	WH-DEL-01	ITM-SSD-01	0	2	88	f	none	simulated	system_sim
8616	2026-07-13	WH-DEL-01	ITM-HDD-01	0	0	60	f	none	simulated	system_sim
8617	2026-07-13	WH-DEL-01	ITM-CHG-01	0	6	144	f	none	simulated	system_sim
8618	2026-07-13	WH-DEL-01	ITM-CBL-01	0	9	291	f	none	simulated	system_sim
8619	2026-07-13	WH-CCU-01	ITM-CPU-01	0	0	45	f	none	simulated	system_sim
8620	2026-07-13	WH-CCU-01	ITM-GPU-01	0	1	29	f	none	simulated	system_sim
8621	2026-07-13	WH-CCU-01	ITM-RAM-01	0	10	65	f	none	simulated	system_sim
8622	2026-07-13	WH-CCU-01	ITM-SSD-01	0	2	88	f	none	simulated	system_sim
8623	2026-07-13	WH-CCU-01	ITM-HDD-01	0	3	57	f	none	simulated	system_sim
8624	2026-07-13	WH-CCU-01	ITM-CHG-01	0	10	140	f	none	simulated	system_sim
8625	2026-07-13	WH-CCU-01	ITM-CBL-01	0	10	290	f	none	simulated	system_sim
8626	2026-07-14	WH-BLR-01	ITM-CPU-01	0	3	39	f	none	simulated	system_sim
8627	2026-07-14	WH-BLR-01	ITM-GPU-01	0	0	30	f	none	simulated	system_sim
8628	2026-07-14	WH-BLR-01	ITM-RAM-01	0	9	65	f	none	simulated	system_sim
8629	2026-07-14	WH-BLR-01	ITM-SSD-01	0	2	86	f	none	simulated	system_sim
8630	2026-07-14	WH-BLR-01	ITM-HDD-01	0	3	57	f	none	simulated	system_sim
8631	2026-07-14	WH-BLR-01	ITM-CHG-01	0	3	137	f	none	simulated	system_sim
8632	2026-07-14	WH-BLR-01	ITM-CBL-01	0	8	284	f	none	simulated	system_sim
8633	2026-07-14	WH-CHN-01	ITM-CPU-01	0	1	42	f	none	simulated	system_sim
8634	2026-07-14	WH-CHN-01	ITM-GPU-01	0	0	30	f	none	simulated	system_sim
8635	2026-07-14	WH-CHN-01	ITM-RAM-01	0	10	63	f	none	simulated	system_sim
8636	2026-07-14	WH-CHN-01	ITM-SSD-01	0	2	88	f	none	simulated	system_sim
8637	2026-07-14	WH-CHN-01	ITM-HDD-01	0	2	57	f	none	simulated	system_sim
8638	2026-07-14	WH-CHN-01	ITM-CHG-01	0	5	139	f	none	simulated	system_sim
8639	2026-07-14	WH-CHN-01	ITM-CBL-01	0	6	286	f	none	simulated	system_sim
8640	2026-07-14	WH-BOM-01	ITM-CPU-01	0	3	41	f	none	simulated	system_sim
8641	2026-07-14	WH-BOM-01	ITM-GPU-01	0	0	28	f	none	simulated	system_sim
8642	2026-07-14	WH-BOM-01	ITM-RAM-01	0	10	60	f	none	simulated	system_sim
8643	2026-07-14	WH-BOM-01	ITM-SSD-01	0	0	88	f	none	simulated	system_sim
8644	2026-07-14	WH-BOM-01	ITM-HDD-01	0	0	59	f	none	simulated	system_sim
8645	2026-07-14	WH-BOM-01	ITM-CHG-01	0	4	143	f	none	simulated	system_sim
8646	2026-07-14	WH-BOM-01	ITM-CBL-01	0	10	289	f	none	simulated	system_sim
8647	2026-07-14	WH-DEL-01	ITM-CPU-01	0	2	41	f	none	simulated	system_sim
8648	2026-07-14	WH-DEL-01	ITM-GPU-01	0	0	30	f	none	simulated	system_sim
8649	2026-07-14	WH-DEL-01	ITM-RAM-01	0	9	65	f	none	simulated	system_sim
8650	2026-07-14	WH-DEL-01	ITM-SSD-01	0	1	87	f	none	simulated	system_sim
8651	2026-07-14	WH-DEL-01	ITM-HDD-01	0	3	57	f	none	simulated	system_sim
8652	2026-07-14	WH-DEL-01	ITM-CHG-01	0	1	143	f	none	simulated	system_sim
8653	2026-07-14	WH-DEL-01	ITM-CBL-01	0	3	288	f	none	simulated	system_sim
8654	2026-07-14	WH-CCU-01	ITM-CPU-01	0	0	45	f	none	simulated	system_sim
8655	2026-07-14	WH-CCU-01	ITM-GPU-01	0	2	27	f	none	simulated	system_sim
8656	2026-07-14	WH-CCU-01	ITM-RAM-01	0	9	56	f	none	simulated	system_sim
8657	2026-07-14	WH-CCU-01	ITM-SSD-01	0	3	85	f	none	simulated	system_sim
8658	2026-07-14	WH-CCU-01	ITM-HDD-01	0	0	57	f	none	simulated	system_sim
8659	2026-07-14	WH-CCU-01	ITM-CHG-01	0	1	139	f	none	simulated	system_sim
8660	2026-07-14	WH-CCU-01	ITM-CBL-01	0	5	285	f	none	simulated	system_sim
8661	2026-07-15	WH-BLR-01	ITM-CPU-01	0	1	38	f	none	simulated	system_sim
8662	2026-07-15	WH-BLR-01	ITM-GPU-01	0	0	30	f	none	simulated	system_sim
8663	2026-07-15	WH-BLR-01	ITM-RAM-01	0	1	64	f	none	simulated	system_sim
8664	2026-07-15	WH-BLR-01	ITM-SSD-01	0	3	83	f	none	simulated	system_sim
8665	2026-07-15	WH-BLR-01	ITM-HDD-01	0	0	57	f	none	simulated	system_sim
8666	2026-07-15	WH-BLR-01	ITM-CHG-01	0	1	136	f	none	simulated	system_sim
8667	2026-07-15	WH-BLR-01	ITM-CBL-01	0	7	277	f	none	simulated	system_sim
8668	2026-07-15	WH-CHN-01	ITM-CPU-01	0	0	42	f	none	simulated	system_sim
8669	2026-07-15	WH-CHN-01	ITM-GPU-01	0	2	28	f	none	simulated	system_sim
8670	2026-07-15	WH-CHN-01	ITM-RAM-01	0	1	62	f	none	simulated	system_sim
8671	2026-07-15	WH-CHN-01	ITM-SSD-01	0	3	85	f	none	simulated	system_sim
8672	2026-07-15	WH-CHN-01	ITM-HDD-01	0	3	54	f	none	simulated	system_sim
8673	2026-07-15	WH-CHN-01	ITM-CHG-01	0	2	137	f	none	simulated	system_sim
8674	2026-07-15	WH-CHN-01	ITM-CBL-01	0	7	279	f	none	simulated	system_sim
8675	2026-07-15	WH-BOM-01	ITM-CPU-01	0	0	41	f	none	simulated	system_sim
8676	2026-07-15	WH-BOM-01	ITM-GPU-01	0	2	26	f	none	simulated	system_sim
8677	2026-07-15	WH-BOM-01	ITM-RAM-01	0	7	53	f	none	simulated	system_sim
8678	2026-07-15	WH-BOM-01	ITM-SSD-01	0	3	85	f	none	simulated	system_sim
8679	2026-07-15	WH-BOM-01	ITM-HDD-01	0	3	56	f	none	simulated	system_sim
8680	2026-07-15	WH-BOM-01	ITM-CHG-01	0	1	142	f	none	simulated	system_sim
8681	2026-07-15	WH-BOM-01	ITM-CBL-01	0	9	280	f	none	simulated	system_sim
8682	2026-07-15	WH-DEL-01	ITM-CPU-01	0	0	41	f	none	simulated	system_sim
8683	2026-07-15	WH-DEL-01	ITM-GPU-01	0	0	30	f	none	simulated	system_sim
8684	2026-07-15	WH-DEL-01	ITM-RAM-01	0	6	59	f	none	simulated	system_sim
8685	2026-07-15	WH-DEL-01	ITM-SSD-01	0	1	86	f	none	simulated	system_sim
8686	2026-07-15	WH-DEL-01	ITM-HDD-01	0	3	54	f	none	simulated	system_sim
8687	2026-07-15	WH-DEL-01	ITM-CHG-01	0	6	137	f	none	simulated	system_sim
8688	2026-07-15	WH-DEL-01	ITM-CBL-01	0	6	282	f	none	simulated	system_sim
8689	2026-07-15	WH-CCU-01	ITM-CPU-01	0	2	43	f	none	simulated	system_sim
8690	2026-07-15	WH-CCU-01	ITM-GPU-01	0	1	26	f	none	simulated	system_sim
8691	2026-07-15	WH-CCU-01	ITM-RAM-01	0	3	53	f	none	simulated	system_sim
8692	2026-07-15	WH-CCU-01	ITM-SSD-01	0	1	84	f	none	simulated	system_sim
8693	2026-07-15	WH-CCU-01	ITM-HDD-01	0	3	54	f	none	simulated	system_sim
8694	2026-07-15	WH-CCU-01	ITM-CHG-01	0	10	129	f	none	simulated	system_sim
8695	2026-07-15	WH-CCU-01	ITM-CBL-01	0	9	276	f	none	simulated	system_sim
8696	2026-07-16	WH-BLR-01	ITM-CPU-01	0	0	38	f	none	simulated	system_sim
8697	2026-07-16	WH-BLR-01	ITM-GPU-01	0	0	30	f	none	simulated	system_sim
8698	2026-07-16	WH-BLR-01	ITM-RAM-01	0	3	61	f	none	simulated	system_sim
8699	2026-07-16	WH-BLR-01	ITM-SSD-01	0	2	81	f	none	simulated	system_sim
8700	2026-07-16	WH-BLR-01	ITM-HDD-01	0	2	55	f	none	simulated	system_sim
8701	2026-07-16	WH-BLR-01	ITM-CHG-01	0	10	126	f	none	simulated	system_sim
8702	2026-07-16	WH-BLR-01	ITM-CBL-01	0	9	268	f	none	simulated	system_sim
8703	2026-07-16	WH-CHN-01	ITM-CPU-01	0	2	40	f	none	simulated	system_sim
8704	2026-07-16	WH-CHN-01	ITM-GPU-01	0	0	28	f	none	simulated	system_sim
8705	2026-07-16	WH-CHN-01	ITM-RAM-01	0	2	60	f	none	simulated	system_sim
8706	2026-07-16	WH-CHN-01	ITM-SSD-01	0	1	84	f	none	simulated	system_sim
8707	2026-07-16	WH-CHN-01	ITM-HDD-01	0	1	53	f	none	simulated	system_sim
8708	2026-07-16	WH-CHN-01	ITM-CHG-01	0	4	133	f	none	simulated	system_sim
8709	2026-07-16	WH-CHN-01	ITM-CBL-01	0	3	276	f	none	simulated	system_sim
8710	2026-07-16	WH-BOM-01	ITM-CPU-01	0	3	38	f	none	simulated	system_sim
8711	2026-07-16	WH-BOM-01	ITM-GPU-01	0	2	24	f	none	simulated	system_sim
8712	2026-07-16	WH-BOM-01	ITM-RAM-01	0	6	47	f	none	simulated	system_sim
8713	2026-07-16	WH-BOM-01	ITM-SSD-01	0	0	85	f	none	simulated	system_sim
8714	2026-07-16	WH-BOM-01	ITM-HDD-01	0	0	56	f	none	simulated	system_sim
8715	2026-07-16	WH-BOM-01	ITM-CHG-01	0	10	132	f	none	simulated	system_sim
8716	2026-07-16	WH-BOM-01	ITM-CBL-01	0	4	276	f	none	simulated	system_sim
8717	2026-07-16	WH-DEL-01	ITM-CPU-01	0	2	39	f	none	simulated	system_sim
8718	2026-07-16	WH-DEL-01	ITM-GPU-01	0	0	30	f	none	simulated	system_sim
8719	2026-07-16	WH-DEL-01	ITM-RAM-01	0	6	53	f	none	simulated	system_sim
8720	2026-07-16	WH-DEL-01	ITM-SSD-01	0	0	86	f	none	simulated	system_sim
8721	2026-07-16	WH-DEL-01	ITM-HDD-01	0	3	51	f	none	simulated	system_sim
8722	2026-07-16	WH-DEL-01	ITM-CHG-01	0	1	136	f	none	simulated	system_sim
8723	2026-07-16	WH-DEL-01	ITM-CBL-01	0	3	279	f	none	simulated	system_sim
8724	2026-07-16	WH-CCU-01	ITM-CPU-01	0	0	43	f	none	simulated	system_sim
8725	2026-07-16	WH-CCU-01	ITM-GPU-01	0	0	26	f	none	simulated	system_sim
8726	2026-07-16	WH-CCU-01	ITM-RAM-01	0	9	44	f	none	simulated	system_sim
8727	2026-07-16	WH-CCU-01	ITM-SSD-01	0	0	84	f	none	simulated	system_sim
8728	2026-07-16	WH-CCU-01	ITM-HDD-01	0	1	53	f	none	simulated	system_sim
8729	2026-07-16	WH-CCU-01	ITM-CHG-01	0	4	125	f	none	simulated	system_sim
8730	2026-07-16	WH-CCU-01	ITM-CBL-01	0	8	268	f	none	simulated	system_sim
8731	2026-07-17	WH-BLR-01	ITM-CPU-01	0	1	37	f	none	simulated	system_sim
8732	2026-07-17	WH-BLR-01	ITM-GPU-01	0	2	28	f	none	simulated	system_sim
8733	2026-07-17	WH-BLR-01	ITM-RAM-01	0	9	52	f	none	simulated	system_sim
8734	2026-07-17	WH-BLR-01	ITM-SSD-01	0	1	80	f	none	simulated	system_sim
8735	2026-07-17	WH-BLR-01	ITM-HDD-01	0	0	55	f	none	simulated	system_sim
8736	2026-07-17	WH-BLR-01	ITM-CHG-01	0	9	117	f	none	simulated	system_sim
8737	2026-07-17	WH-BLR-01	ITM-CBL-01	0	4	264	f	none	simulated	system_sim
8738	2026-07-17	WH-CHN-01	ITM-CPU-01	0	0	40	f	none	simulated	system_sim
8739	2026-07-17	WH-CHN-01	ITM-GPU-01	0	0	28	f	none	simulated	system_sim
8740	2026-07-17	WH-CHN-01	ITM-RAM-01	0	10	50	f	none	simulated	system_sim
8741	2026-07-17	WH-CHN-01	ITM-SSD-01	0	3	81	f	none	simulated	system_sim
8742	2026-07-17	WH-CHN-01	ITM-HDD-01	0	0	53	f	none	simulated	system_sim
8743	2026-07-17	WH-CHN-01	ITM-CHG-01	0	1	132	f	none	simulated	system_sim
8744	2026-07-17	WH-CHN-01	ITM-CBL-01	0	7	269	f	none	simulated	system_sim
8745	2026-07-17	WH-BOM-01	ITM-CPU-01	0	2	36	f	none	simulated	system_sim
8746	2026-07-17	WH-BOM-01	ITM-GPU-01	0	1	23	f	none	simulated	system_sim
8747	2026-07-17	WH-BOM-01	ITM-RAM-01	0	8	39	f	none	simulated	system_sim
8748	2026-07-17	WH-BOM-01	ITM-SSD-01	0	0	85	f	none	simulated	system_sim
8749	2026-07-17	WH-BOM-01	ITM-HDD-01	0	1	55	f	none	simulated	system_sim
8750	2026-07-17	WH-BOM-01	ITM-CHG-01	0	7	125	f	none	simulated	system_sim
8751	2026-07-17	WH-BOM-01	ITM-CBL-01	0	2	274	f	none	simulated	system_sim
8752	2026-07-17	WH-DEL-01	ITM-CPU-01	0	0	39	f	none	simulated	system_sim
8753	2026-07-17	WH-DEL-01	ITM-GPU-01	0	1	29	f	none	simulated	system_sim
8754	2026-07-17	WH-DEL-01	ITM-RAM-01	0	5	48	f	none	simulated	system_sim
8755	2026-07-17	WH-DEL-01	ITM-SSD-01	0	1	85	f	none	simulated	system_sim
8756	2026-07-17	WH-DEL-01	ITM-HDD-01	0	2	49	f	none	simulated	system_sim
8757	2026-07-17	WH-DEL-01	ITM-CHG-01	0	5	131	f	none	simulated	system_sim
8758	2026-07-17	WH-DEL-01	ITM-CBL-01	0	3	276	f	none	simulated	system_sim
8759	2026-07-17	WH-CCU-01	ITM-CPU-01	0	1	42	f	none	simulated	system_sim
8760	2026-07-17	WH-CCU-01	ITM-GPU-01	0	0	26	f	none	simulated	system_sim
8761	2026-07-17	WH-CCU-01	ITM-RAM-01	0	1	43	f	none	simulated	system_sim
8762	2026-07-17	WH-CCU-01	ITM-SSD-01	0	3	81	f	none	simulated	system_sim
8763	2026-07-17	WH-CCU-01	ITM-HDD-01	0	2	51	f	none	simulated	system_sim
8764	2026-07-17	WH-CCU-01	ITM-CHG-01	0	8	117	f	none	simulated	system_sim
8765	2026-07-17	WH-CCU-01	ITM-CBL-01	0	4	264	f	none	simulated	system_sim
8766	2026-07-18	WH-BLR-01	ITM-CPU-01	0	0	37	f	none	simulated	system_sim
8767	2026-07-18	WH-BLR-01	ITM-GPU-01	0	2	26	f	none	simulated	system_sim
8768	2026-07-18	WH-BLR-01	ITM-RAM-01	0	6	46	f	none	simulated	system_sim
8769	2026-07-18	WH-BLR-01	ITM-SSD-01	0	0	80	f	none	simulated	system_sim
8770	2026-07-18	WH-BLR-01	ITM-HDD-01	0	0	55	f	none	simulated	system_sim
8771	2026-07-18	WH-BLR-01	ITM-CHG-01	0	7	110	f	none	simulated	system_sim
8772	2026-07-18	WH-BLR-01	ITM-CBL-01	0	3	261	f	none	simulated	system_sim
8773	2026-07-18	WH-CHN-01	ITM-CPU-01	0	1	39	f	none	simulated	system_sim
8774	2026-07-18	WH-CHN-01	ITM-GPU-01	0	1	27	f	none	simulated	system_sim
8775	2026-07-18	WH-CHN-01	ITM-RAM-01	0	5	45	f	none	simulated	system_sim
8776	2026-07-18	WH-CHN-01	ITM-SSD-01	0	0	81	f	none	simulated	system_sim
8777	2026-07-18	WH-CHN-01	ITM-HDD-01	0	3	50	f	none	simulated	system_sim
8778	2026-07-18	WH-CHN-01	ITM-CHG-01	0	8	124	f	none	simulated	system_sim
8779	2026-07-18	WH-CHN-01	ITM-CBL-01	0	3	266	f	none	simulated	system_sim
8780	2026-07-18	WH-BOM-01	ITM-CPU-01	0	0	36	f	none	simulated	system_sim
8781	2026-07-18	WH-BOM-01	ITM-GPU-01	0	0	23	f	none	simulated	system_sim
8782	2026-07-18	WH-BOM-01	ITM-RAM-01	0	9	30	f	none	simulated	system_sim
8783	2026-07-18	WH-BOM-01	ITM-SSD-01	0	0	85	f	none	simulated	system_sim
8784	2026-07-18	WH-BOM-01	ITM-HDD-01	0	2	53	f	none	simulated	system_sim
8785	2026-07-18	WH-BOM-01	ITM-CHG-01	0	6	119	f	none	simulated	system_sim
8786	2026-07-18	WH-BOM-01	ITM-CBL-01	0	5	269	f	none	simulated	system_sim
8787	2026-07-18	WH-DEL-01	ITM-CPU-01	0	0	39	f	none	simulated	system_sim
8788	2026-07-18	WH-DEL-01	ITM-GPU-01	0	0	29	f	none	simulated	system_sim
8789	2026-07-18	WH-DEL-01	ITM-RAM-01	0	9	39	f	none	simulated	system_sim
8790	2026-07-18	WH-DEL-01	ITM-SSD-01	0	0	85	f	none	simulated	system_sim
8791	2026-07-18	WH-DEL-01	ITM-HDD-01	0	0	49	f	none	simulated	system_sim
8792	2026-07-18	WH-DEL-01	ITM-CHG-01	0	6	125	f	none	simulated	system_sim
8793	2026-07-18	WH-DEL-01	ITM-CBL-01	0	4	272	f	none	simulated	system_sim
8794	2026-07-18	WH-CCU-01	ITM-CPU-01	0	0	42	f	none	simulated	system_sim
8795	2026-07-18	WH-CCU-01	ITM-GPU-01	0	1	25	f	none	simulated	system_sim
8796	2026-07-18	WH-CCU-01	ITM-RAM-01	0	10	33	f	none	simulated	system_sim
8797	2026-07-18	WH-CCU-01	ITM-SSD-01	0	2	79	f	none	simulated	system_sim
8798	2026-07-18	WH-CCU-01	ITM-HDD-01	0	2	49	f	none	simulated	system_sim
8799	2026-07-18	WH-CCU-01	ITM-CHG-01	0	6	111	f	none	simulated	system_sim
8800	2026-07-18	WH-CCU-01	ITM-CBL-01	0	6	258	f	none	simulated	system_sim
8801	2026-07-19	WH-BLR-01	ITM-CPU-01	0	0	37	f	none	simulated	system_sim
8802	2026-07-19	WH-BLR-01	ITM-GPU-01	0	0	26	f	none	simulated	system_sim
8803	2026-07-19	WH-BLR-01	ITM-RAM-01	0	3	43	f	none	simulated	system_sim
8804	2026-07-19	WH-BLR-01	ITM-SSD-01	0	0	80	f	none	simulated	system_sim
8805	2026-07-19	WH-BLR-01	ITM-HDD-01	0	0	55	f	none	simulated	system_sim
8806	2026-07-19	WH-BLR-01	ITM-CHG-01	0	10	100	f	none	simulated	system_sim
8807	2026-07-19	WH-BLR-01	ITM-CBL-01	0	10	251	f	none	simulated	system_sim
8808	2026-07-19	WH-CHN-01	ITM-CPU-01	0	0	39	f	none	simulated	system_sim
8809	2026-07-19	WH-CHN-01	ITM-GPU-01	0	0	27	f	none	simulated	system_sim
8810	2026-07-19	WH-CHN-01	ITM-RAM-01	0	9	36	f	none	simulated	system_sim
8811	2026-07-19	WH-CHN-01	ITM-SSD-01	0	0	81	f	none	simulated	system_sim
8812	2026-07-19	WH-CHN-01	ITM-HDD-01	0	0	50	f	none	simulated	system_sim
8813	2026-07-19	WH-CHN-01	ITM-CHG-01	0	7	117	f	none	simulated	system_sim
8814	2026-07-19	WH-CHN-01	ITM-CBL-01	0	4	262	f	none	simulated	system_sim
8815	2026-07-19	WH-BOM-01	ITM-CPU-01	0	0	36	f	none	simulated	system_sim
8816	2026-07-19	WH-BOM-01	ITM-GPU-01	0	0	23	f	none	simulated	system_sim
8817	2026-07-19	WH-BOM-01	ITM-RAM-01	75	5	100	f	none	simulated	system_sim
8818	2026-07-19	WH-BOM-01	ITM-SSD-01	0	0	85	f	none	simulated	system_sim
8819	2026-07-19	WH-BOM-01	ITM-HDD-01	0	1	52	f	none	simulated	system_sim
8820	2026-07-19	WH-BOM-01	ITM-CHG-01	0	6	113	f	none	simulated	system_sim
8821	2026-07-19	WH-BOM-01	ITM-CBL-01	0	1	268	f	none	simulated	system_sim
8822	2026-07-19	WH-DEL-01	ITM-CPU-01	0	0	39	f	none	simulated	system_sim
8823	2026-07-19	WH-DEL-01	ITM-GPU-01	0	2	27	f	none	simulated	system_sim
8824	2026-07-19	WH-DEL-01	ITM-RAM-01	0	4	35	f	none	simulated	system_sim
8825	2026-07-19	WH-DEL-01	ITM-SSD-01	0	0	85	f	none	simulated	system_sim
8826	2026-07-19	WH-DEL-01	ITM-HDD-01	0	3	46	f	none	simulated	system_sim
8827	2026-07-19	WH-DEL-01	ITM-CHG-01	0	4	121	f	none	simulated	system_sim
8828	2026-07-19	WH-DEL-01	ITM-CBL-01	0	7	265	f	none	simulated	system_sim
8829	2026-07-19	WH-CCU-01	ITM-CPU-01	0	2	40	f	none	simulated	system_sim
8830	2026-07-19	WH-CCU-01	ITM-GPU-01	0	0	25	f	none	simulated	system_sim
8831	2026-07-19	WH-CCU-01	ITM-RAM-01	75	4	104	f	none	simulated	system_sim
8832	2026-07-19	WH-CCU-01	ITM-SSD-01	0	1	78	f	none	simulated	system_sim
8833	2026-07-19	WH-CCU-01	ITM-HDD-01	0	0	49	f	none	simulated	system_sim
8834	2026-07-19	WH-CCU-01	ITM-CHG-01	0	3	108	f	none	simulated	system_sim
8835	2026-07-19	WH-CCU-01	ITM-CBL-01	0	10	248	f	none	simulated	system_sim
8836	2026-07-20	WH-BLR-01	ITM-CPU-01	0	2	35	f	none	simulated	system_sim
8837	2026-07-20	WH-BLR-01	ITM-GPU-01	0	1	25	f	none	simulated	system_sim
8838	2026-07-20	WH-BLR-01	ITM-RAM-01	0	9	34	f	none	simulated	system_sim
8839	2026-07-20	WH-BLR-01	ITM-SSD-01	0	0	80	f	none	simulated	system_sim
8840	2026-07-20	WH-BLR-01	ITM-HDD-01	0	3	52	f	none	simulated	system_sim
8841	2026-07-20	WH-BLR-01	ITM-CHG-01	0	1	99	f	none	simulated	system_sim
8842	2026-07-20	WH-BLR-01	ITM-CBL-01	0	8	243	f	none	simulated	system_sim
8843	2026-07-20	WH-CHN-01	ITM-CPU-01	0	2	37	f	none	simulated	system_sim
8844	2026-07-20	WH-CHN-01	ITM-GPU-01	0	0	27	f	none	simulated	system_sim
8845	2026-07-20	WH-CHN-01	ITM-RAM-01	75	8	103	f	none	simulated	system_sim
8846	2026-07-20	WH-CHN-01	ITM-SSD-01	0	2	79	f	none	simulated	system_sim
8847	2026-07-20	WH-CHN-01	ITM-HDD-01	0	0	50	f	none	simulated	system_sim
8848	2026-07-20	WH-CHN-01	ITM-CHG-01	0	10	107	f	none	simulated	system_sim
8849	2026-07-20	WH-CHN-01	ITM-CBL-01	0	7	255	f	none	simulated	system_sim
8850	2026-07-20	WH-BOM-01	ITM-CPU-01	0	3	33	f	none	simulated	system_sim
8851	2026-07-20	WH-BOM-01	ITM-GPU-01	0	0	23	f	none	simulated	system_sim
8852	2026-07-20	WH-BOM-01	ITM-RAM-01	0	9	91	f	none	simulated	system_sim
8853	2026-07-20	WH-BOM-01	ITM-SSD-01	0	2	83	f	none	simulated	system_sim
8854	2026-07-20	WH-BOM-01	ITM-HDD-01	0	2	50	f	none	simulated	system_sim
8855	2026-07-20	WH-BOM-01	ITM-CHG-01	0	9	104	f	none	simulated	system_sim
8856	2026-07-20	WH-BOM-01	ITM-CBL-01	0	8	260	f	none	simulated	system_sim
8857	2026-07-20	WH-DEL-01	ITM-CPU-01	0	0	39	f	none	simulated	system_sim
8858	2026-07-20	WH-DEL-01	ITM-GPU-01	0	0	27	f	none	simulated	system_sim
8859	2026-07-20	WH-DEL-01	ITM-RAM-01	75	3	107	f	none	simulated	system_sim
8860	2026-07-20	WH-DEL-01	ITM-SSD-01	0	2	83	f	none	simulated	system_sim
8861	2026-07-20	WH-DEL-01	ITM-HDD-01	0	1	45	f	none	simulated	system_sim
8862	2026-07-20	WH-DEL-01	ITM-CHG-01	0	8	113	f	none	simulated	system_sim
8863	2026-07-20	WH-DEL-01	ITM-CBL-01	0	3	262	f	none	simulated	system_sim
8864	2026-07-20	WH-CCU-01	ITM-CPU-01	0	0	40	f	none	simulated	system_sim
8865	2026-07-20	WH-CCU-01	ITM-GPU-01	0	1	24	f	none	simulated	system_sim
8866	2026-07-20	WH-CCU-01	ITM-RAM-01	0	2	102	f	none	simulated	system_sim
8867	2026-07-20	WH-CCU-01	ITM-SSD-01	0	0	78	f	none	simulated	system_sim
8868	2026-07-20	WH-CCU-01	ITM-HDD-01	0	2	47	f	none	simulated	system_sim
8869	2026-07-20	WH-CCU-01	ITM-CHG-01	0	9	99	f	none	simulated	system_sim
8870	2026-07-20	WH-CCU-01	ITM-CBL-01	0	6	242	f	none	simulated	system_sim
8871	2026-07-21	WH-BLR-01	ITM-CPU-01	0	1	34	f	none	simulated	system_sim
8872	2026-07-21	WH-BLR-01	ITM-GPU-01	0	2	23	f	none	simulated	system_sim
8873	2026-07-21	WH-BLR-01	ITM-RAM-01	75	5	104	f	none	simulated	system_sim
8874	2026-07-21	WH-BLR-01	ITM-SSD-01	0	2	78	f	none	simulated	system_sim
8875	2026-07-21	WH-BLR-01	ITM-HDD-01	0	0	52	f	none	simulated	system_sim
8876	2026-07-21	WH-BLR-01	ITM-CHG-01	0	7	92	f	none	simulated	system_sim
8877	2026-07-21	WH-BLR-01	ITM-CBL-01	0	10	233	f	none	simulated	system_sim
8878	2026-07-21	WH-CHN-01	ITM-CPU-01	0	1	36	f	none	simulated	system_sim
8879	2026-07-21	WH-CHN-01	ITM-GPU-01	0	0	27	f	none	simulated	system_sim
8880	2026-07-21	WH-CHN-01	ITM-RAM-01	0	2	101	f	none	simulated	system_sim
8881	2026-07-21	WH-CHN-01	ITM-SSD-01	0	0	79	f	none	simulated	system_sim
8882	2026-07-21	WH-CHN-01	ITM-HDD-01	0	2	48	f	none	simulated	system_sim
8883	2026-07-21	WH-CHN-01	ITM-CHG-01	0	4	103	f	none	simulated	system_sim
8884	2026-07-21	WH-CHN-01	ITM-CBL-01	0	6	249	f	none	simulated	system_sim
8885	2026-07-21	WH-BOM-01	ITM-CPU-01	0	0	33	f	none	simulated	system_sim
8886	2026-07-21	WH-BOM-01	ITM-GPU-01	0	1	22	f	none	simulated	system_sim
8887	2026-07-21	WH-BOM-01	ITM-RAM-01	0	9	82	f	none	simulated	system_sim
8888	2026-07-21	WH-BOM-01	ITM-SSD-01	0	1	82	f	none	simulated	system_sim
8889	2026-07-21	WH-BOM-01	ITM-HDD-01	0	2	48	f	none	simulated	system_sim
8890	2026-07-21	WH-BOM-01	ITM-CHG-01	0	1	103	f	none	simulated	system_sim
8891	2026-07-21	WH-BOM-01	ITM-CBL-01	0	8	252	f	none	simulated	system_sim
8892	2026-07-21	WH-DEL-01	ITM-CPU-01	0	2	37	f	none	simulated	system_sim
8893	2026-07-21	WH-DEL-01	ITM-GPU-01	0	0	27	f	none	simulated	system_sim
8894	2026-07-21	WH-DEL-01	ITM-RAM-01	0	3	104	f	none	simulated	system_sim
8895	2026-07-21	WH-DEL-01	ITM-SSD-01	0	2	81	f	none	simulated	system_sim
8896	2026-07-21	WH-DEL-01	ITM-HDD-01	0	0	45	f	none	simulated	system_sim
8897	2026-07-21	WH-DEL-01	ITM-CHG-01	0	1	112	f	none	simulated	system_sim
8898	2026-07-21	WH-DEL-01	ITM-CBL-01	0	10	252	f	none	simulated	system_sim
8899	2026-07-21	WH-CCU-01	ITM-CPU-01	0	1	39	f	none	simulated	system_sim
8900	2026-07-21	WH-CCU-01	ITM-GPU-01	0	1	23	f	none	simulated	system_sim
8901	2026-07-21	WH-CCU-01	ITM-RAM-01	0	3	99	f	none	simulated	system_sim
8902	2026-07-21	WH-CCU-01	ITM-SSD-01	0	3	75	f	none	simulated	system_sim
8903	2026-07-21	WH-CCU-01	ITM-HDD-01	0	0	47	f	none	simulated	system_sim
8904	2026-07-21	WH-CCU-01	ITM-CHG-01	0	1	98	f	none	simulated	system_sim
8905	2026-07-21	WH-CCU-01	ITM-CBL-01	0	1	241	f	none	simulated	system_sim
8906	2026-07-22	WH-BLR-01	ITM-CPU-01	0	0	34	f	none	simulated	system_sim
8907	2026-07-22	WH-BLR-01	ITM-GPU-01	0	0	23	f	none	simulated	system_sim
8908	2026-07-22	WH-BLR-01	ITM-RAM-01	0	9	95	f	none	simulated	system_sim
8909	2026-07-22	WH-BLR-01	ITM-SSD-01	0	3	75	f	none	simulated	system_sim
8910	2026-07-22	WH-BLR-01	ITM-HDD-01	0	0	52	f	none	simulated	system_sim
8911	2026-07-22	WH-BLR-01	ITM-CHG-01	0	4	88	f	none	simulated	system_sim
8912	2026-07-22	WH-BLR-01	ITM-CBL-01	0	4	229	f	none	simulated	system_sim
8913	2026-07-22	WH-CHN-01	ITM-CPU-01	0	3	33	f	none	simulated	system_sim
8914	2026-07-22	WH-CHN-01	ITM-GPU-01	0	0	27	f	none	simulated	system_sim
8915	2026-07-22	WH-CHN-01	ITM-RAM-01	0	1	100	f	none	simulated	system_sim
8916	2026-07-22	WH-CHN-01	ITM-SSD-01	0	0	79	f	none	simulated	system_sim
8917	2026-07-22	WH-CHN-01	ITM-HDD-01	0	1	47	f	none	simulated	system_sim
8918	2026-07-22	WH-CHN-01	ITM-CHG-01	0	7	96	f	none	simulated	system_sim
8919	2026-07-22	WH-CHN-01	ITM-CBL-01	0	9	240	f	none	simulated	system_sim
8920	2026-07-22	WH-BOM-01	ITM-CPU-01	0	1	32	f	none	simulated	system_sim
8921	2026-07-22	WH-BOM-01	ITM-GPU-01	0	0	22	f	none	simulated	system_sim
8922	2026-07-22	WH-BOM-01	ITM-RAM-01	0	6	76	f	none	simulated	system_sim
8923	2026-07-22	WH-BOM-01	ITM-SSD-01	0	0	82	f	none	simulated	system_sim
8924	2026-07-22	WH-BOM-01	ITM-HDD-01	0	0	48	f	none	simulated	system_sim
8925	2026-07-22	WH-BOM-01	ITM-CHG-01	0	3	100	f	none	simulated	system_sim
8926	2026-07-22	WH-BOM-01	ITM-CBL-01	0	2	250	f	none	simulated	system_sim
8927	2026-07-22	WH-DEL-01	ITM-CPU-01	0	0	37	f	none	simulated	system_sim
8928	2026-07-22	WH-DEL-01	ITM-GPU-01	0	0	27	f	none	simulated	system_sim
8929	2026-07-22	WH-DEL-01	ITM-RAM-01	0	10	94	f	none	simulated	system_sim
8930	2026-07-22	WH-DEL-01	ITM-SSD-01	0	0	81	f	none	simulated	system_sim
8931	2026-07-22	WH-DEL-01	ITM-HDD-01	0	0	45	f	none	simulated	system_sim
8932	2026-07-22	WH-DEL-01	ITM-CHG-01	0	1	111	f	none	simulated	system_sim
8933	2026-07-22	WH-DEL-01	ITM-CBL-01	0	3	249	f	none	simulated	system_sim
8934	2026-07-22	WH-CCU-01	ITM-CPU-01	0	1	38	f	none	simulated	system_sim
8935	2026-07-22	WH-CCU-01	ITM-GPU-01	0	1	22	f	none	simulated	system_sim
8936	2026-07-22	WH-CCU-01	ITM-RAM-01	0	10	89	f	none	simulated	system_sim
8937	2026-07-22	WH-CCU-01	ITM-SSD-01	0	0	75	f	none	simulated	system_sim
8938	2026-07-22	WH-CCU-01	ITM-HDD-01	0	0	47	f	none	simulated	system_sim
8939	2026-07-22	WH-CCU-01	ITM-CHG-01	0	7	91	f	none	simulated	system_sim
8940	2026-07-22	WH-CCU-01	ITM-CBL-01	0	6	235	f	none	simulated	system_sim
8941	2026-07-23	WH-BLR-01	ITM-CPU-01	0	2	32	f	none	simulated	system_sim
8942	2026-07-23	WH-BLR-01	ITM-GPU-01	0	0	23	f	none	simulated	system_sim
8943	2026-07-23	WH-BLR-01	ITM-RAM-01	0	9	86	f	none	simulated	system_sim
8944	2026-07-23	WH-BLR-01	ITM-SSD-01	0	2	73	f	none	simulated	system_sim
8945	2026-07-23	WH-BLR-01	ITM-HDD-01	0	1	51	f	none	simulated	system_sim
8946	2026-07-23	WH-BLR-01	ITM-CHG-01	0	6	82	f	none	simulated	system_sim
8947	2026-07-23	WH-BLR-01	ITM-CBL-01	0	8	221	f	none	simulated	system_sim
8948	2026-07-23	WH-CHN-01	ITM-CPU-01	0	0	33	f	none	simulated	system_sim
8949	2026-07-23	WH-CHN-01	ITM-GPU-01	0	0	27	f	none	simulated	system_sim
8950	2026-07-23	WH-CHN-01	ITM-RAM-01	0	1	99	f	none	simulated	system_sim
8951	2026-07-23	WH-CHN-01	ITM-SSD-01	0	2	77	f	none	simulated	system_sim
8952	2026-07-23	WH-CHN-01	ITM-HDD-01	0	1	46	f	none	simulated	system_sim
8953	2026-07-23	WH-CHN-01	ITM-CHG-01	0	9	87	f	none	simulated	system_sim
8954	2026-07-23	WH-CHN-01	ITM-CBL-01	0	4	236	f	none	simulated	system_sim
8955	2026-07-23	WH-BOM-01	ITM-CPU-01	0	2	30	f	none	simulated	system_sim
8956	2026-07-23	WH-BOM-01	ITM-GPU-01	0	0	22	f	none	simulated	system_sim
8957	2026-07-23	WH-BOM-01	ITM-RAM-01	0	2	74	f	none	simulated	system_sim
8958	2026-07-23	WH-BOM-01	ITM-SSD-01	0	0	82	f	none	simulated	system_sim
8959	2026-07-23	WH-BOM-01	ITM-HDD-01	0	0	48	f	none	simulated	system_sim
8960	2026-07-23	WH-BOM-01	ITM-CHG-01	0	3	97	f	none	simulated	system_sim
8961	2026-07-23	WH-BOM-01	ITM-CBL-01	0	9	241	f	none	simulated	system_sim
8962	2026-07-23	WH-DEL-01	ITM-CPU-01	0	3	34	f	none	simulated	system_sim
8963	2026-07-23	WH-DEL-01	ITM-GPU-01	0	1	26	f	none	simulated	system_sim
8964	2026-07-23	WH-DEL-01	ITM-RAM-01	0	4	90	f	none	simulated	system_sim
8965	2026-07-23	WH-DEL-01	ITM-SSD-01	0	1	80	f	none	simulated	system_sim
8966	2026-07-23	WH-DEL-01	ITM-HDD-01	0	0	45	f	none	simulated	system_sim
8967	2026-07-23	WH-DEL-01	ITM-CHG-01	0	8	103	f	none	simulated	system_sim
8968	2026-07-23	WH-DEL-01	ITM-CBL-01	0	3	246	f	none	simulated	system_sim
8969	2026-07-23	WH-CCU-01	ITM-CPU-01	0	0	38	f	none	simulated	system_sim
8970	2026-07-23	WH-CCU-01	ITM-GPU-01	0	0	22	f	none	simulated	system_sim
8971	2026-07-23	WH-CCU-01	ITM-RAM-01	0	3	86	f	none	simulated	system_sim
8972	2026-07-23	WH-CCU-01	ITM-SSD-01	0	3	72	f	none	simulated	system_sim
8973	2026-07-23	WH-CCU-01	ITM-HDD-01	0	1	46	f	none	simulated	system_sim
8974	2026-07-23	WH-CCU-01	ITM-CHG-01	0	6	85	f	none	simulated	system_sim
8975	2026-07-23	WH-CCU-01	ITM-CBL-01	0	8	227	f	none	simulated	system_sim
8976	2026-07-24	WH-BLR-01	ITM-CPU-01	0	2	30	f	none	simulated	system_sim
8977	2026-07-24	WH-BLR-01	ITM-GPU-01	0	0	23	f	none	simulated	system_sim
8978	2026-07-24	WH-BLR-01	ITM-RAM-01	0	6	80	f	none	simulated	system_sim
8979	2026-07-24	WH-BLR-01	ITM-SSD-01	0	0	73	f	none	simulated	system_sim
8980	2026-07-24	WH-BLR-01	ITM-HDD-01	0	1	50	f	none	simulated	system_sim
8981	2026-07-24	WH-BLR-01	ITM-CHG-01	0	1	81	f	none	simulated	system_sim
8982	2026-07-24	WH-BLR-01	ITM-CBL-01	0	3	218	f	none	simulated	system_sim
8983	2026-07-24	WH-CHN-01	ITM-CPU-01	0	2	31	f	none	simulated	system_sim
8984	2026-07-24	WH-CHN-01	ITM-GPU-01	0	0	27	f	none	simulated	system_sim
8985	2026-07-24	WH-CHN-01	ITM-RAM-01	0	10	89	f	none	simulated	system_sim
8986	2026-07-24	WH-CHN-01	ITM-SSD-01	0	0	77	f	none	simulated	system_sim
8987	2026-07-24	WH-CHN-01	ITM-HDD-01	0	2	44	f	none	simulated	system_sim
8988	2026-07-24	WH-CHN-01	ITM-CHG-01	0	1	86	f	none	simulated	system_sim
8989	2026-07-24	WH-CHN-01	ITM-CBL-01	0	6	230	f	none	simulated	system_sim
8990	2026-07-24	WH-BOM-01	ITM-CPU-01	0	1	29	f	none	simulated	system_sim
8991	2026-07-24	WH-BOM-01	ITM-GPU-01	0	2	20	f	none	simulated	system_sim
8992	2026-07-24	WH-BOM-01	ITM-RAM-01	0	8	66	f	none	simulated	system_sim
8993	2026-07-24	WH-BOM-01	ITM-SSD-01	0	2	80	f	none	simulated	system_sim
8994	2026-07-24	WH-BOM-01	ITM-HDD-01	0	3	45	f	none	simulated	system_sim
8995	2026-07-24	WH-BOM-01	ITM-CHG-01	0	8	89	f	none	simulated	system_sim
8996	2026-07-24	WH-BOM-01	ITM-CBL-01	0	9	232	f	none	simulated	system_sim
8997	2026-07-24	WH-DEL-01	ITM-CPU-01	0	3	31	f	none	simulated	system_sim
8998	2026-07-24	WH-DEL-01	ITM-GPU-01	0	0	26	f	none	simulated	system_sim
8999	2026-07-24	WH-DEL-01	ITM-RAM-01	0	6	84	f	none	simulated	system_sim
9000	2026-07-24	WH-DEL-01	ITM-SSD-01	0	0	80	f	none	simulated	system_sim
9001	2026-07-24	WH-DEL-01	ITM-HDD-01	0	1	44	f	none	simulated	system_sim
9002	2026-07-24	WH-DEL-01	ITM-CHG-01	0	10	93	f	none	simulated	system_sim
9003	2026-07-24	WH-DEL-01	ITM-CBL-01	0	10	236	f	none	simulated	system_sim
9004	2026-07-24	WH-CCU-01	ITM-CPU-01	0	2	36	f	none	simulated	system_sim
9005	2026-07-24	WH-CCU-01	ITM-GPU-01	0	1	21	f	none	simulated	system_sim
9006	2026-07-24	WH-CCU-01	ITM-RAM-01	0	6	80	f	none	simulated	system_sim
9007	2026-07-24	WH-CCU-01	ITM-SSD-01	0	1	71	f	none	simulated	system_sim
9008	2026-07-24	WH-CCU-01	ITM-HDD-01	0	2	44	f	none	simulated	system_sim
9009	2026-07-24	WH-CCU-01	ITM-CHG-01	0	1	84	f	none	simulated	system_sim
9010	2026-07-24	WH-CCU-01	ITM-CBL-01	0	3	224	f	none	simulated	system_sim
9011	2026-07-25	WH-BLR-01	ITM-CPU-01	0	2	28	f	none	simulated	system_sim
9012	2026-07-25	WH-BLR-01	ITM-GPU-01	0	1	22	f	none	simulated	system_sim
9013	2026-07-25	WH-BLR-01	ITM-RAM-01	0	4	76	f	none	simulated	system_sim
9014	2026-07-25	WH-BLR-01	ITM-SSD-01	0	0	73	f	none	simulated	system_sim
9015	2026-07-25	WH-BLR-01	ITM-HDD-01	0	1	49	f	none	simulated	system_sim
9016	2026-07-25	WH-BLR-01	ITM-CHG-01	0	10	71	f	none	simulated	system_sim
9017	2026-07-25	WH-BLR-01	ITM-CBL-01	0	9	209	f	none	simulated	system_sim
9018	2026-07-25	WH-CHN-01	ITM-CPU-01	0	0	16	t	shrinkage	simulated	system_sim
9019	2026-07-25	WH-CHN-01	ITM-GPU-01	0	0	27	f	none	simulated	system_sim
9020	2026-07-25	WH-CHN-01	ITM-RAM-01	0	3	86	f	none	simulated	system_sim
9021	2026-07-25	WH-CHN-01	ITM-SSD-01	0	0	77	f	none	simulated	system_sim
9022	2026-07-25	WH-CHN-01	ITM-HDD-01	0	2	42	f	none	simulated	system_sim
9023	2026-07-25	WH-CHN-01	ITM-CHG-01	0	2	84	f	none	simulated	system_sim
9024	2026-07-25	WH-CHN-01	ITM-CBL-01	0	4	226	f	none	simulated	system_sim
9025	2026-07-25	WH-BOM-01	ITM-CPU-01	0	0	29	f	none	simulated	system_sim
9026	2026-07-25	WH-BOM-01	ITM-GPU-01	0	0	20	f	none	simulated	system_sim
9027	2026-07-25	WH-BOM-01	ITM-RAM-01	0	7	59	f	none	simulated	system_sim
9028	2026-07-25	WH-BOM-01	ITM-SSD-01	0	2	78	f	none	simulated	system_sim
9029	2026-07-25	WH-BOM-01	ITM-HDD-01	0	1	44	f	none	simulated	system_sim
9030	2026-07-25	WH-BOM-01	ITM-CHG-01	0	10	79	f	none	simulated	system_sim
9031	2026-07-25	WH-BOM-01	ITM-CBL-01	0	1	231	f	none	simulated	system_sim
9032	2026-07-25	WH-DEL-01	ITM-CPU-01	0	1	30	f	none	simulated	system_sim
9033	2026-07-25	WH-DEL-01	ITM-GPU-01	0	2	24	f	none	simulated	system_sim
9034	2026-07-25	WH-DEL-01	ITM-RAM-01	0	1	83	f	none	simulated	system_sim
9035	2026-07-25	WH-DEL-01	ITM-SSD-01	0	3	77	f	none	simulated	system_sim
9036	2026-07-25	WH-DEL-01	ITM-HDD-01	0	2	42	f	none	simulated	system_sim
9037	2026-07-25	WH-DEL-01	ITM-CHG-01	0	1	92	f	none	simulated	system_sim
9038	2026-07-25	WH-DEL-01	ITM-CBL-01	0	8	228	f	none	simulated	system_sim
9039	2026-07-25	WH-CCU-01	ITM-CPU-01	0	2	34	f	none	simulated	system_sim
9040	2026-07-25	WH-CCU-01	ITM-GPU-01	0	0	21	f	none	simulated	system_sim
9041	2026-07-25	WH-CCU-01	ITM-RAM-01	0	6	74	f	none	simulated	system_sim
9042	2026-07-25	WH-CCU-01	ITM-SSD-01	0	1	70	f	none	simulated	system_sim
9043	2026-07-25	WH-CCU-01	ITM-HDD-01	0	1	43	f	none	simulated	system_sim
9044	2026-07-25	WH-CCU-01	ITM-CHG-01	0	3	81	f	none	simulated	system_sim
9045	2026-07-25	WH-CCU-01	ITM-CBL-01	0	10	214	f	none	simulated	system_sim
9046	2026-07-26	WH-BLR-01	ITM-CPU-01	0	0	28	f	none	simulated	system_sim
9047	2026-07-26	WH-BLR-01	ITM-GPU-01	0	1	21	f	none	simulated	system_sim
9048	2026-07-26	WH-BLR-01	ITM-RAM-01	0	1	75	f	none	simulated	system_sim
9049	2026-07-26	WH-BLR-01	ITM-SSD-01	0	0	73	f	none	simulated	system_sim
9050	2026-07-26	WH-BLR-01	ITM-HDD-01	0	0	49	f	none	simulated	system_sim
9051	2026-07-26	WH-BLR-01	ITM-CHG-01	150	2	219	f	none	simulated	system_sim
9052	2026-07-26	WH-BLR-01	ITM-CBL-01	0	1	208	f	none	simulated	system_sim
9053	2026-07-26	WH-CHN-01	ITM-CPU-01	45	3	58	f	none	simulated	system_sim
9054	2026-07-26	WH-CHN-01	ITM-GPU-01	0	2	25	f	none	simulated	system_sim
9055	2026-07-26	WH-CHN-01	ITM-RAM-01	0	8	78	f	none	simulated	system_sim
9056	2026-07-26	WH-CHN-01	ITM-SSD-01	0	0	77	f	none	simulated	system_sim
9057	2026-07-26	WH-CHN-01	ITM-HDD-01	0	1	41	f	none	simulated	system_sim
9058	2026-07-26	WH-CHN-01	ITM-CHG-01	0	8	76	f	none	simulated	system_sim
9059	2026-07-26	WH-CHN-01	ITM-CBL-01	0	6	220	f	none	simulated	system_sim
9060	2026-07-26	WH-BOM-01	ITM-CPU-01	0	2	27	f	none	simulated	system_sim
9061	2026-07-26	WH-BOM-01	ITM-GPU-01	0	2	18	f	none	simulated	system_sim
9062	2026-07-26	WH-BOM-01	ITM-RAM-01	0	9	50	f	none	simulated	system_sim
9063	2026-07-26	WH-BOM-01	ITM-SSD-01	0	0	78	f	none	simulated	system_sim
9064	2026-07-26	WH-BOM-01	ITM-HDD-01	0	2	42	f	none	simulated	system_sim
9065	2026-07-26	WH-BOM-01	ITM-CHG-01	0	3	76	f	none	simulated	system_sim
9066	2026-07-26	WH-BOM-01	ITM-CBL-01	0	7	224	f	none	simulated	system_sim
9067	2026-07-26	WH-DEL-01	ITM-CPU-01	0	0	30	f	none	simulated	system_sim
9068	2026-07-26	WH-DEL-01	ITM-GPU-01	0	1	23	f	none	simulated	system_sim
9069	2026-07-26	WH-DEL-01	ITM-RAM-01	0	8	75	f	none	simulated	system_sim
9070	2026-07-26	WH-DEL-01	ITM-SSD-01	0	0	77	f	none	simulated	system_sim
9071	2026-07-26	WH-DEL-01	ITM-HDD-01	0	0	42	f	none	simulated	system_sim
9072	2026-07-26	WH-DEL-01	ITM-CHG-01	0	4	88	f	none	simulated	system_sim
9073	2026-07-26	WH-DEL-01	ITM-CBL-01	0	5	223	f	none	simulated	system_sim
9074	2026-07-26	WH-CCU-01	ITM-CPU-01	0	3	31	f	none	simulated	system_sim
9075	2026-07-26	WH-CCU-01	ITM-GPU-01	0	0	21	f	none	simulated	system_sim
9076	2026-07-26	WH-CCU-01	ITM-RAM-01	0	10	64	f	none	simulated	system_sim
9077	2026-07-26	WH-CCU-01	ITM-SSD-01	0	1	69	f	none	simulated	system_sim
9078	2026-07-26	WH-CCU-01	ITM-HDD-01	0	2	41	f	none	simulated	system_sim
9079	2026-07-26	WH-CCU-01	ITM-CHG-01	0	3	78	f	none	simulated	system_sim
9080	2026-07-26	WH-CCU-01	ITM-CBL-01	0	5	209	f	none	simulated	system_sim
9081	2026-07-27	WH-BLR-01	ITM-CPU-01	0	2	26	f	none	simulated	system_sim
9082	2026-07-27	WH-BLR-01	ITM-GPU-01	0	1	20	f	none	simulated	system_sim
9083	2026-07-27	WH-BLR-01	ITM-RAM-01	0	1	74	f	none	simulated	system_sim
9084	2026-07-27	WH-BLR-01	ITM-SSD-01	0	1	72	f	none	simulated	system_sim
9085	2026-07-27	WH-BLR-01	ITM-HDD-01	0	0	49	f	none	simulated	system_sim
9086	2026-07-27	WH-BLR-01	ITM-CHG-01	0	4	215	f	none	simulated	system_sim
9087	2026-07-27	WH-BLR-01	ITM-CBL-01	0	10	198	f	none	simulated	system_sim
9088	2026-07-27	WH-CHN-01	ITM-CPU-01	0	2	56	f	none	simulated	system_sim
9089	2026-07-27	WH-CHN-01	ITM-GPU-01	0	0	25	f	none	simulated	system_sim
9090	2026-07-27	WH-CHN-01	ITM-RAM-01	0	10	68	f	none	simulated	system_sim
9091	2026-07-27	WH-CHN-01	ITM-SSD-01	0	1	76	f	none	simulated	system_sim
9092	2026-07-27	WH-CHN-01	ITM-HDD-01	0	0	41	f	none	simulated	system_sim
9093	2026-07-27	WH-CHN-01	ITM-CHG-01	0	5	71	f	none	simulated	system_sim
9094	2026-07-27	WH-CHN-01	ITM-CBL-01	0	4	216	f	none	simulated	system_sim
9095	2026-07-27	WH-BOM-01	ITM-CPU-01	0	0	27	f	none	simulated	system_sim
9096	2026-07-27	WH-BOM-01	ITM-GPU-01	0	2	16	f	none	simulated	system_sim
9097	2026-07-27	WH-BOM-01	ITM-RAM-01	0	2	48	f	none	simulated	system_sim
9098	2026-07-27	WH-BOM-01	ITM-SSD-01	0	3	75	f	none	simulated	system_sim
9099	2026-07-27	WH-BOM-01	ITM-HDD-01	0	0	42	f	none	simulated	system_sim
9100	2026-07-27	WH-BOM-01	ITM-CHG-01	0	4	72	f	none	simulated	system_sim
9101	2026-07-27	WH-BOM-01	ITM-CBL-01	0	1	223	f	none	simulated	system_sim
9102	2026-07-27	WH-DEL-01	ITM-CPU-01	0	0	30	f	none	simulated	system_sim
9103	2026-07-27	WH-DEL-01	ITM-GPU-01	0	0	23	f	none	simulated	system_sim
9104	2026-07-27	WH-DEL-01	ITM-RAM-01	0	1	74	f	none	simulated	system_sim
9105	2026-07-27	WH-DEL-01	ITM-SSD-01	0	1	76	f	none	simulated	system_sim
9106	2026-07-27	WH-DEL-01	ITM-HDD-01	0	3	39	f	none	simulated	system_sim
9107	2026-07-27	WH-DEL-01	ITM-CHG-01	0	2	86	f	none	simulated	system_sim
9108	2026-07-27	WH-DEL-01	ITM-CBL-01	0	4	219	f	none	simulated	system_sim
9109	2026-07-27	WH-CCU-01	ITM-CPU-01	0	0	31	f	none	simulated	system_sim
9110	2026-07-27	WH-CCU-01	ITM-GPU-01	0	0	21	f	none	simulated	system_sim
9111	2026-07-27	WH-CCU-01	ITM-RAM-01	0	3	61	f	none	simulated	system_sim
9112	2026-07-27	WH-CCU-01	ITM-SSD-01	0	0	69	f	none	simulated	system_sim
9113	2026-07-27	WH-CCU-01	ITM-HDD-01	0	2	39	f	none	simulated	system_sim
9114	2026-07-27	WH-CCU-01	ITM-CHG-01	0	5	73	f	none	simulated	system_sim
9115	2026-07-27	WH-CCU-01	ITM-CBL-01	0	2	207	f	none	simulated	system_sim
9116	2026-07-28	WH-BLR-01	ITM-CPU-01	0	0	26	f	none	simulated	system_sim
9117	2026-07-28	WH-BLR-01	ITM-GPU-01	0	0	20	f	none	simulated	system_sim
9118	2026-07-28	WH-BLR-01	ITM-RAM-01	0	7	67	f	none	simulated	system_sim
9119	2026-07-28	WH-BLR-01	ITM-SSD-01	0	0	72	f	none	simulated	system_sim
9120	2026-07-28	WH-BLR-01	ITM-HDD-01	0	3	46	f	none	simulated	system_sim
9121	2026-07-28	WH-BLR-01	ITM-CHG-01	0	1	214	f	none	simulated	system_sim
9122	2026-07-28	WH-BLR-01	ITM-CBL-01	0	6	192	f	none	simulated	system_sim
9123	2026-07-28	WH-CHN-01	ITM-CPU-01	0	3	53	f	none	simulated	system_sim
9124	2026-07-28	WH-CHN-01	ITM-GPU-01	0	0	25	f	none	simulated	system_sim
9125	2026-07-28	WH-CHN-01	ITM-RAM-01	0	5	63	f	none	simulated	system_sim
9126	2026-07-28	WH-CHN-01	ITM-SSD-01	0	3	73	f	none	simulated	system_sim
9127	2026-07-28	WH-CHN-01	ITM-HDD-01	0	3	38	f	none	simulated	system_sim
9128	2026-07-28	WH-CHN-01	ITM-CHG-01	150	6	215	f	none	simulated	system_sim
9129	2026-07-28	WH-CHN-01	ITM-CBL-01	0	4	212	f	none	simulated	system_sim
9130	2026-07-28	WH-BOM-01	ITM-CPU-01	0	0	27	f	none	simulated	system_sim
9131	2026-07-28	WH-BOM-01	ITM-GPU-01	0	0	16	f	none	simulated	system_sim
9132	2026-07-28	WH-BOM-01	ITM-RAM-01	0	8	40	f	none	simulated	system_sim
9133	2026-07-28	WH-BOM-01	ITM-SSD-01	0	0	75	f	none	simulated	system_sim
9134	2026-07-28	WH-BOM-01	ITM-HDD-01	0	0	42	f	none	simulated	system_sim
9135	2026-07-28	WH-BOM-01	ITM-CHG-01	150	3	219	f	none	simulated	system_sim
9136	2026-07-28	WH-BOM-01	ITM-CBL-01	0	8	215	f	none	simulated	system_sim
9137	2026-07-28	WH-DEL-01	ITM-CPU-01	0	1	29	f	none	simulated	system_sim
9138	2026-07-28	WH-DEL-01	ITM-GPU-01	0	0	23	f	none	simulated	system_sim
9139	2026-07-28	WH-DEL-01	ITM-RAM-01	0	5	69	f	none	simulated	system_sim
9140	2026-07-28	WH-DEL-01	ITM-SSD-01	0	3	73	f	none	simulated	system_sim
9141	2026-07-28	WH-DEL-01	ITM-HDD-01	0	2	37	f	none	simulated	system_sim
9142	2026-07-28	WH-DEL-01	ITM-CHG-01	0	10	76	f	none	simulated	system_sim
9143	2026-07-28	WH-DEL-01	ITM-CBL-01	0	9	210	f	none	simulated	system_sim
9144	2026-07-28	WH-CCU-01	ITM-CPU-01	0	0	31	f	none	simulated	system_sim
9145	2026-07-28	WH-CCU-01	ITM-GPU-01	0	0	21	f	none	simulated	system_sim
9146	2026-07-28	WH-CCU-01	ITM-RAM-01	0	9	52	f	none	simulated	system_sim
9147	2026-07-28	WH-CCU-01	ITM-SSD-01	0	2	67	f	none	simulated	system_sim
9148	2026-07-28	WH-CCU-01	ITM-HDD-01	0	1	38	f	none	simulated	system_sim
9149	2026-07-28	WH-CCU-01	ITM-CHG-01	150	6	217	f	none	simulated	system_sim
9150	2026-07-28	WH-CCU-01	ITM-CBL-01	0	6	201	f	none	simulated	system_sim
9151	2026-07-29	WH-BLR-01	ITM-CPU-01	0	0	26	f	none	simulated	system_sim
9152	2026-07-29	WH-BLR-01	ITM-GPU-01	0	0	20	f	none	simulated	system_sim
9153	2026-07-29	WH-BLR-01	ITM-RAM-01	0	8	59	f	none	simulated	system_sim
9154	2026-07-29	WH-BLR-01	ITM-SSD-01	0	2	70	f	none	simulated	system_sim
9155	2026-07-29	WH-BLR-01	ITM-HDD-01	0	1	45	f	none	simulated	system_sim
9156	2026-07-29	WH-BLR-01	ITM-CHG-01	0	2	212	f	none	simulated	system_sim
9157	2026-07-29	WH-BLR-01	ITM-CBL-01	0	1	191	f	none	simulated	system_sim
9158	2026-07-29	WH-CHN-01	ITM-CPU-01	0	0	53	f	none	simulated	system_sim
9159	2026-07-29	WH-CHN-01	ITM-GPU-01	0	1	24	f	none	simulated	system_sim
9160	2026-07-29	WH-CHN-01	ITM-RAM-01	0	8	55	f	none	simulated	system_sim
9161	2026-07-29	WH-CHN-01	ITM-SSD-01	0	3	70	f	none	simulated	system_sim
9162	2026-07-29	WH-CHN-01	ITM-HDD-01	0	2	36	f	none	simulated	system_sim
9163	2026-07-29	WH-CHN-01	ITM-CHG-01	0	2	213	f	none	simulated	system_sim
9164	2026-07-29	WH-CHN-01	ITM-CBL-01	0	6	206	f	none	simulated	system_sim
9165	2026-07-29	WH-BOM-01	ITM-CPU-01	0	0	27	f	none	simulated	system_sim
9166	2026-07-29	WH-BOM-01	ITM-GPU-01	0	0	16	f	none	simulated	system_sim
9167	2026-07-29	WH-BOM-01	ITM-RAM-01	0	10	30	f	none	simulated	system_sim
9168	2026-07-29	WH-BOM-01	ITM-SSD-01	0	3	72	f	none	simulated	system_sim
9169	2026-07-29	WH-BOM-01	ITM-HDD-01	0	2	40	f	none	simulated	system_sim
9170	2026-07-29	WH-BOM-01	ITM-CHG-01	0	8	211	f	none	simulated	system_sim
9171	2026-07-29	WH-BOM-01	ITM-CBL-01	0	5	210	f	none	simulated	system_sim
9172	2026-07-29	WH-DEL-01	ITM-CPU-01	0	2	27	f	none	simulated	system_sim
9173	2026-07-29	WH-DEL-01	ITM-GPU-01	0	0	23	f	none	simulated	system_sim
9174	2026-07-29	WH-DEL-01	ITM-RAM-01	0	9	60	f	none	simulated	system_sim
9175	2026-07-29	WH-DEL-01	ITM-SSD-01	0	3	70	f	none	simulated	system_sim
9176	2026-07-29	WH-DEL-01	ITM-HDD-01	0	0	37	f	none	simulated	system_sim
9177	2026-07-29	WH-DEL-01	ITM-CHG-01	0	9	67	f	none	simulated	system_sim
9178	2026-07-29	WH-DEL-01	ITM-CBL-01	0	4	206	f	none	simulated	system_sim
9179	2026-07-29	WH-CCU-01	ITM-CPU-01	0	0	31	f	none	simulated	system_sim
9180	2026-07-29	WH-CCU-01	ITM-GPU-01	0	0	21	f	none	simulated	system_sim
9181	2026-07-29	WH-CCU-01	ITM-RAM-01	0	4	48	f	none	simulated	system_sim
9182	2026-07-29	WH-CCU-01	ITM-SSD-01	0	3	64	f	none	simulated	system_sim
9183	2026-07-29	WH-CCU-01	ITM-HDD-01	0	2	36	f	none	simulated	system_sim
9184	2026-07-29	WH-CCU-01	ITM-CHG-01	0	10	207	f	none	simulated	system_sim
9185	2026-07-29	WH-CCU-01	ITM-CBL-01	0	3	198	f	none	simulated	system_sim
9186	2026-07-30	WH-BLR-01	ITM-CPU-01	0	0	26	f	none	simulated	system_sim
9187	2026-07-30	WH-BLR-01	ITM-GPU-01	0	1	19	f	none	simulated	system_sim
9188	2026-07-30	WH-BLR-01	ITM-RAM-01	0	4	55	f	none	simulated	system_sim
9189	2026-07-30	WH-BLR-01	ITM-SSD-01	0	2	68	f	none	simulated	system_sim
9190	2026-07-30	WH-BLR-01	ITM-HDD-01	0	2	43	f	none	simulated	system_sim
9191	2026-07-30	WH-BLR-01	ITM-CHG-01	0	1	211	f	none	simulated	system_sim
9192	2026-07-30	WH-BLR-01	ITM-CBL-01	0	3	188	f	none	simulated	system_sim
9193	2026-07-30	WH-CHN-01	ITM-CPU-01	0	3	50	f	none	simulated	system_sim
9194	2026-07-30	WH-CHN-01	ITM-GPU-01	0	0	24	f	none	simulated	system_sim
9195	2026-07-30	WH-CHN-01	ITM-RAM-01	0	2	53	f	none	simulated	system_sim
9196	2026-07-30	WH-CHN-01	ITM-SSD-01	0	0	70	f	none	simulated	system_sim
9197	2026-07-30	WH-CHN-01	ITM-HDD-01	0	3	33	f	none	simulated	system_sim
9198	2026-07-30	WH-CHN-01	ITM-CHG-01	0	5	208	f	none	simulated	system_sim
9199	2026-07-30	WH-CHN-01	ITM-CBL-01	0	6	200	f	none	simulated	system_sim
9200	2026-07-30	WH-BOM-01	ITM-CPU-01	0	2	25	f	none	simulated	system_sim
9201	2026-07-30	WH-BOM-01	ITM-GPU-01	0	1	15	f	none	simulated	system_sim
9202	2026-07-30	WH-BOM-01	ITM-RAM-01	75	4	101	f	none	simulated	system_sim
9203	2026-07-30	WH-BOM-01	ITM-SSD-01	0	3	69	f	none	simulated	system_sim
9204	2026-07-30	WH-BOM-01	ITM-HDD-01	0	1	39	f	none	simulated	system_sim
9205	2026-07-30	WH-BOM-01	ITM-CHG-01	0	9	202	f	none	simulated	system_sim
9206	2026-07-30	WH-BOM-01	ITM-CBL-01	0	2	208	f	none	simulated	system_sim
9207	2026-07-30	WH-DEL-01	ITM-CPU-01	0	2	25	f	none	simulated	system_sim
9208	2026-07-30	WH-DEL-01	ITM-GPU-01	0	2	21	f	none	simulated	system_sim
9209	2026-07-30	WH-DEL-01	ITM-RAM-01	0	5	55	f	none	simulated	system_sim
9210	2026-07-30	WH-DEL-01	ITM-SSD-01	0	0	70	f	none	simulated	system_sim
9211	2026-07-30	WH-DEL-01	ITM-HDD-01	0	3	34	f	none	simulated	system_sim
9212	2026-07-30	WH-DEL-01	ITM-CHG-01	150	3	214	f	none	simulated	system_sim
9213	2026-07-30	WH-DEL-01	ITM-CBL-01	0	8	198	f	none	simulated	system_sim
9214	2026-07-30	WH-CCU-01	ITM-CPU-01	0	0	31	f	none	simulated	system_sim
9215	2026-07-30	WH-CCU-01	ITM-GPU-01	0	2	19	f	none	simulated	system_sim
9216	2026-07-30	WH-CCU-01	ITM-RAM-01	0	6	42	f	none	simulated	system_sim
9217	2026-07-30	WH-CCU-01	ITM-SSD-01	0	0	64	f	none	simulated	system_sim
9218	2026-07-30	WH-CCU-01	ITM-HDD-01	0	1	35	f	none	simulated	system_sim
9219	2026-07-30	WH-CCU-01	ITM-CHG-01	0	5	202	f	none	simulated	system_sim
9220	2026-07-30	WH-CCU-01	ITM-CBL-01	0	3	195	f	none	simulated	system_sim
9221	2026-07-31	WH-BLR-01	ITM-CPU-01	0	0	26	f	none	simulated	system_sim
9222	2026-07-31	WH-BLR-01	ITM-GPU-01	0	0	19	f	none	simulated	system_sim
9223	2026-07-31	WH-BLR-01	ITM-RAM-01	0	9	46	f	none	simulated	system_sim
9224	2026-07-31	WH-BLR-01	ITM-SSD-01	0	3	65	f	none	simulated	system_sim
9225	2026-07-31	WH-BLR-01	ITM-HDD-01	0	3	40	f	none	simulated	system_sim
9226	2026-07-31	WH-BLR-01	ITM-CHG-01	0	10	201	f	none	simulated	system_sim
9227	2026-07-31	WH-BLR-01	ITM-CBL-01	0	9	179	f	none	simulated	system_sim
9228	2026-07-31	WH-CHN-01	ITM-CPU-01	0	1	49	f	none	simulated	system_sim
9229	2026-07-31	WH-CHN-01	ITM-GPU-01	0	0	24	f	none	simulated	system_sim
9230	2026-07-31	WH-CHN-01	ITM-RAM-01	0	6	47	f	none	simulated	system_sim
9231	2026-07-31	WH-CHN-01	ITM-SSD-01	0	3	67	f	none	simulated	system_sim
9232	2026-07-31	WH-CHN-01	ITM-HDD-01	0	3	30	f	none	simulated	system_sim
9233	2026-07-31	WH-CHN-01	ITM-CHG-01	0	4	204	f	none	simulated	system_sim
9234	2026-07-31	WH-CHN-01	ITM-CBL-01	0	4	196	f	none	simulated	system_sim
9235	2026-07-31	WH-BOM-01	ITM-CPU-01	0	0	25	f	none	simulated	system_sim
9236	2026-07-31	WH-BOM-01	ITM-GPU-01	0	0	15	f	none	simulated	system_sim
9237	2026-07-31	WH-BOM-01	ITM-RAM-01	0	7	94	f	none	simulated	system_sim
9238	2026-07-31	WH-BOM-01	ITM-SSD-01	0	0	69	f	none	simulated	system_sim
9239	2026-07-31	WH-BOM-01	ITM-HDD-01	0	0	39	f	none	simulated	system_sim
9240	2026-07-31	WH-BOM-01	ITM-CHG-01	0	2	200	f	none	simulated	system_sim
9241	2026-07-31	WH-BOM-01	ITM-CBL-01	0	2	206	f	none	simulated	system_sim
9242	2026-07-31	WH-DEL-01	ITM-CPU-01	0	0	25	f	none	simulated	system_sim
9243	2026-07-31	WH-DEL-01	ITM-GPU-01	0	0	21	f	none	simulated	system_sim
9244	2026-07-31	WH-DEL-01	ITM-RAM-01	0	10	45	f	none	simulated	system_sim
9245	2026-07-31	WH-DEL-01	ITM-SSD-01	0	3	67	f	none	simulated	system_sim
9246	2026-07-31	WH-DEL-01	ITM-HDD-01	0	0	34	f	none	simulated	system_sim
9247	2026-07-31	WH-DEL-01	ITM-CHG-01	0	10	204	f	none	simulated	system_sim
9248	2026-07-31	WH-DEL-01	ITM-CBL-01	0	2	196	f	none	simulated	system_sim
9249	2026-07-31	WH-CCU-01	ITM-CPU-01	0	0	31	f	none	simulated	system_sim
9250	2026-07-31	WH-CCU-01	ITM-GPU-01	0	1	18	f	none	simulated	system_sim
9251	2026-07-31	WH-CCU-01	ITM-RAM-01	0	7	35	f	none	simulated	system_sim
9252	2026-07-31	WH-CCU-01	ITM-SSD-01	0	2	62	f	none	simulated	system_sim
9253	2026-07-31	WH-CCU-01	ITM-HDD-01	0	0	35	f	none	simulated	system_sim
9254	2026-07-31	WH-CCU-01	ITM-CHG-01	0	4	198	f	none	simulated	system_sim
9255	2026-07-31	WH-CCU-01	ITM-CBL-01	0	1	194	f	none	simulated	system_sim
9256	2026-08-01	WH-BLR-01	ITM-CPU-01	0	0	26	f	none	simulated	system_sim
9257	2026-08-01	WH-BLR-01	ITM-GPU-01	0	0	19	f	none	simulated	system_sim
9258	2026-08-01	WH-BLR-01	ITM-RAM-01	0	10	36	f	none	simulated	system_sim
9259	2026-08-01	WH-BLR-01	ITM-SSD-01	0	1	64	f	none	simulated	system_sim
9260	2026-08-01	WH-BLR-01	ITM-HDD-01	0	3	37	f	none	simulated	system_sim
9261	2026-08-01	WH-BLR-01	ITM-CHG-01	0	4	197	f	none	simulated	system_sim
9262	2026-08-01	WH-BLR-01	ITM-CBL-01	0	5	174	f	none	simulated	system_sim
9263	2026-08-01	WH-CHN-01	ITM-CPU-01	0	1	48	f	none	simulated	system_sim
9264	2026-08-01	WH-CHN-01	ITM-GPU-01	0	1	23	f	none	simulated	system_sim
9265	2026-08-01	WH-CHN-01	ITM-RAM-01	0	8	39	f	none	simulated	system_sim
9266	2026-08-01	WH-CHN-01	ITM-SSD-01	0	2	65	f	none	simulated	system_sim
9267	2026-08-01	WH-CHN-01	ITM-HDD-01	0	1	29	f	none	simulated	system_sim
9268	2026-08-01	WH-CHN-01	ITM-CHG-01	0	3	201	f	none	simulated	system_sim
9269	2026-08-01	WH-CHN-01	ITM-CBL-01	0	6	190	f	none	simulated	system_sim
9270	2026-08-01	WH-BOM-01	ITM-CPU-01	0	3	22	f	none	simulated	system_sim
9271	2026-08-01	WH-BOM-01	ITM-GPU-01	0	0	15	f	none	simulated	system_sim
9272	2026-08-01	WH-BOM-01	ITM-RAM-01	0	8	86	f	none	simulated	system_sim
9273	2026-08-01	WH-BOM-01	ITM-SSD-01	0	1	68	f	none	simulated	system_sim
9274	2026-08-01	WH-BOM-01	ITM-HDD-01	0	0	39	f	none	simulated	system_sim
9275	2026-08-01	WH-BOM-01	ITM-CHG-01	0	4	196	f	none	simulated	system_sim
9276	2026-08-01	WH-BOM-01	ITM-CBL-01	0	9	197	f	none	simulated	system_sim
9277	2026-08-01	WH-DEL-01	ITM-CPU-01	0	1	24	f	none	simulated	system_sim
9278	2026-08-01	WH-DEL-01	ITM-GPU-01	0	0	21	f	none	simulated	system_sim
9279	2026-08-01	WH-DEL-01	ITM-RAM-01	0	3	42	f	none	simulated	system_sim
9280	2026-08-01	WH-DEL-01	ITM-SSD-01	0	3	64	f	none	simulated	system_sim
9281	2026-08-01	WH-DEL-01	ITM-HDD-01	0	0	34	f	none	simulated	system_sim
9282	2026-08-01	WH-DEL-01	ITM-CHG-01	0	4	200	f	none	simulated	system_sim
9283	2026-08-01	WH-DEL-01	ITM-CBL-01	0	1	195	f	none	simulated	system_sim
9284	2026-08-01	WH-CCU-01	ITM-CPU-01	0	1	30	f	none	simulated	system_sim
9285	2026-08-01	WH-CCU-01	ITM-GPU-01	0	0	18	f	none	simulated	system_sim
9286	2026-08-01	WH-CCU-01	ITM-RAM-01	75	6	104	f	none	simulated	system_sim
9287	2026-08-01	WH-CCU-01	ITM-SSD-01	0	0	62	f	none	simulated	system_sim
9288	2026-08-01	WH-CCU-01	ITM-HDD-01	0	1	34	f	none	simulated	system_sim
9289	2026-08-01	WH-CCU-01	ITM-CHG-01	0	6	192	f	none	simulated	system_sim
9290	2026-08-01	WH-CCU-01	ITM-CBL-01	0	9	185	f	none	simulated	system_sim
9291	2026-08-02	WH-BLR-01	ITM-CPU-01	0	0	26	f	none	simulated	system_sim
9292	2026-08-02	WH-BLR-01	ITM-GPU-01	0	1	18	f	none	simulated	system_sim
9293	2026-08-02	WH-BLR-01	ITM-RAM-01	75	2	109	f	none	simulated	system_sim
9294	2026-08-02	WH-BLR-01	ITM-SSD-01	0	3	61	f	none	simulated	system_sim
9295	2026-08-02	WH-BLR-01	ITM-HDD-01	0	3	34	f	none	simulated	system_sim
9296	2026-08-02	WH-BLR-01	ITM-CHG-01	0	4	193	f	none	simulated	system_sim
9297	2026-08-02	WH-BLR-01	ITM-CBL-01	0	10	164	f	none	simulated	system_sim
9298	2026-08-02	WH-CHN-01	ITM-CPU-01	0	0	48	f	none	simulated	system_sim
9299	2026-08-02	WH-CHN-01	ITM-GPU-01	0	0	23	f	none	simulated	system_sim
9300	2026-08-02	WH-CHN-01	ITM-RAM-01	0	3	36	f	none	simulated	system_sim
9301	2026-08-02	WH-CHN-01	ITM-SSD-01	0	1	64	f	none	simulated	system_sim
9302	2026-08-02	WH-CHN-01	ITM-HDD-01	60	2	87	f	none	simulated	system_sim
9303	2026-08-02	WH-CHN-01	ITM-CHG-01	0	3	198	f	none	simulated	system_sim
9304	2026-08-02	WH-CHN-01	ITM-CBL-01	0	7	183	f	none	simulated	system_sim
9305	2026-08-02	WH-BOM-01	ITM-CPU-01	45	0	67	f	none	simulated	system_sim
9306	2026-08-02	WH-BOM-01	ITM-GPU-01	0	1	14	f	none	simulated	system_sim
9307	2026-08-02	WH-BOM-01	ITM-RAM-01	0	7	79	f	none	simulated	system_sim
9308	2026-08-02	WH-BOM-01	ITM-SSD-01	0	1	67	f	none	simulated	system_sim
9309	2026-08-02	WH-BOM-01	ITM-HDD-01	0	0	39	f	none	simulated	system_sim
9310	2026-08-02	WH-BOM-01	ITM-CHG-01	0	7	189	f	none	simulated	system_sim
9311	2026-08-02	WH-BOM-01	ITM-CBL-01	0	7	190	f	none	simulated	system_sim
9312	2026-08-02	WH-DEL-01	ITM-CPU-01	0	2	22	f	none	simulated	system_sim
9313	2026-08-02	WH-DEL-01	ITM-GPU-01	0	2	19	f	none	simulated	system_sim
9314	2026-08-02	WH-DEL-01	ITM-RAM-01	0	4	38	f	none	simulated	system_sim
9315	2026-08-02	WH-DEL-01	ITM-SSD-01	0	3	61	f	none	simulated	system_sim
9316	2026-08-02	WH-DEL-01	ITM-HDD-01	0	1	33	f	none	simulated	system_sim
9317	2026-08-02	WH-DEL-01	ITM-CHG-01	0	3	197	f	none	simulated	system_sim
9318	2026-08-02	WH-DEL-01	ITM-CBL-01	0	7	188	f	none	simulated	system_sim
9319	2026-08-02	WH-CCU-01	ITM-CPU-01	0	1	29	f	none	simulated	system_sim
9320	2026-08-02	WH-CCU-01	ITM-GPU-01	0	0	18	f	none	simulated	system_sim
9321	2026-08-02	WH-CCU-01	ITM-RAM-01	0	2	102	f	none	simulated	system_sim
9322	2026-08-02	WH-CCU-01	ITM-SSD-01	0	3	59	f	none	simulated	system_sim
9323	2026-08-02	WH-CCU-01	ITM-HDD-01	0	1	33	f	none	simulated	system_sim
9324	2026-08-02	WH-CCU-01	ITM-CHG-01	0	7	185	f	none	simulated	system_sim
9325	2026-08-02	WH-CCU-01	ITM-CBL-01	0	3	182	f	none	simulated	system_sim
9326	2026-08-03	WH-BLR-01	ITM-CPU-01	0	1	25	f	none	simulated	system_sim
9327	2026-08-03	WH-BLR-01	ITM-GPU-01	0	1	17	f	none	simulated	system_sim
9328	2026-08-03	WH-BLR-01	ITM-RAM-01	0	1	108	f	none	simulated	system_sim
9329	2026-08-03	WH-BLR-01	ITM-SSD-01	0	1	60	f	none	simulated	system_sim
9330	2026-08-03	WH-BLR-01	ITM-HDD-01	0	0	34	f	none	simulated	system_sim
9331	2026-08-03	WH-BLR-01	ITM-CHG-01	0	1	192	f	none	simulated	system_sim
9332	2026-08-03	WH-BLR-01	ITM-CBL-01	0	3	161	f	none	simulated	system_sim
9333	2026-08-03	WH-CHN-01	ITM-CPU-01	0	1	47	f	none	simulated	system_sim
9334	2026-08-03	WH-CHN-01	ITM-GPU-01	0	0	23	f	none	simulated	system_sim
9335	2026-08-03	WH-CHN-01	ITM-RAM-01	75	5	106	f	none	simulated	system_sim
9336	2026-08-03	WH-CHN-01	ITM-SSD-01	0	0	64	f	none	simulated	system_sim
9337	2026-08-03	WH-CHN-01	ITM-HDD-01	0	2	85	f	none	simulated	system_sim
9338	2026-08-03	WH-CHN-01	ITM-CHG-01	0	3	195	f	none	simulated	system_sim
9339	2026-08-03	WH-CHN-01	ITM-CBL-01	0	7	176	f	none	simulated	system_sim
9340	2026-08-03	WH-BOM-01	ITM-CPU-01	0	0	67	f	none	simulated	system_sim
9341	2026-08-03	WH-BOM-01	ITM-GPU-01	30	0	44	f	none	simulated	system_sim
9342	2026-08-03	WH-BOM-01	ITM-RAM-01	0	4	75	f	none	simulated	system_sim
9343	2026-08-03	WH-BOM-01	ITM-SSD-01	0	3	64	f	none	simulated	system_sim
9344	2026-08-03	WH-BOM-01	ITM-HDD-01	0	0	39	f	none	simulated	system_sim
9345	2026-08-03	WH-BOM-01	ITM-CHG-01	0	4	185	f	none	simulated	system_sim
9346	2026-08-03	WH-BOM-01	ITM-CBL-01	0	2	188	f	none	simulated	system_sim
9347	2026-08-03	WH-DEL-01	ITM-CPU-01	45	3	64	f	none	simulated	system_sim
9348	2026-08-03	WH-DEL-01	ITM-GPU-01	0	1	18	f	none	simulated	system_sim
9349	2026-08-03	WH-DEL-01	ITM-RAM-01	0	7	31	f	none	simulated	system_sim
9350	2026-08-03	WH-DEL-01	ITM-SSD-01	0	0	61	f	none	simulated	system_sim
9351	2026-08-03	WH-DEL-01	ITM-HDD-01	0	0	33	f	none	simulated	system_sim
9352	2026-08-03	WH-DEL-01	ITM-CHG-01	0	7	190	f	none	simulated	system_sim
9353	2026-08-03	WH-DEL-01	ITM-CBL-01	0	1	187	f	none	simulated	system_sim
9354	2026-08-03	WH-CCU-01	ITM-CPU-01	0	3	26	f	none	simulated	system_sim
9355	2026-08-03	WH-CCU-01	ITM-GPU-01	0	0	18	f	none	simulated	system_sim
9356	2026-08-03	WH-CCU-01	ITM-RAM-01	0	3	99	f	none	simulated	system_sim
9357	2026-08-03	WH-CCU-01	ITM-SSD-01	0	3	56	f	none	simulated	system_sim
9358	2026-08-03	WH-CCU-01	ITM-HDD-01	0	1	32	f	none	simulated	system_sim
9359	2026-08-03	WH-CCU-01	ITM-CHG-01	0	1	184	f	none	simulated	system_sim
9360	2026-08-03	WH-CCU-01	ITM-CBL-01	0	8	174	f	none	simulated	system_sim
9361	2026-08-04	WH-BLR-01	ITM-CPU-01	0	2	23	f	none	simulated	system_sim
9362	2026-08-04	WH-BLR-01	ITM-GPU-01	0	0	17	f	none	simulated	system_sim
9363	2026-08-04	WH-BLR-01	ITM-RAM-01	0	1	107	f	none	simulated	system_sim
9364	2026-08-04	WH-BLR-01	ITM-SSD-01	0	0	60	f	none	simulated	system_sim
9365	2026-08-04	WH-BLR-01	ITM-HDD-01	0	0	34	f	none	simulated	system_sim
9366	2026-08-04	WH-BLR-01	ITM-CHG-01	0	2	190	f	none	simulated	system_sim
9367	2026-08-04	WH-BLR-01	ITM-CBL-01	0	5	156	f	none	simulated	system_sim
9368	2026-08-04	WH-CHN-01	ITM-CPU-01	0	1	46	f	none	simulated	system_sim
9369	2026-08-04	WH-CHN-01	ITM-GPU-01	0	0	23	f	none	simulated	system_sim
9370	2026-08-04	WH-CHN-01	ITM-RAM-01	0	6	100	f	none	simulated	system_sim
9371	2026-08-04	WH-CHN-01	ITM-SSD-01	0	0	64	f	none	simulated	system_sim
9372	2026-08-04	WH-CHN-01	ITM-HDD-01	0	0	85	f	none	simulated	system_sim
9373	2026-08-04	WH-CHN-01	ITM-CHG-01	0	9	186	f	none	simulated	system_sim
9374	2026-08-04	WH-CHN-01	ITM-CBL-01	0	9	167	f	none	simulated	system_sim
9375	2026-08-04	WH-BOM-01	ITM-CPU-01	0	2	65	f	none	simulated	system_sim
9376	2026-08-04	WH-BOM-01	ITM-GPU-01	0	1	43	f	none	simulated	system_sim
9377	2026-08-04	WH-BOM-01	ITM-RAM-01	0	9	66	f	none	simulated	system_sim
9378	2026-08-04	WH-BOM-01	ITM-SSD-01	0	0	64	f	none	simulated	system_sim
9379	2026-08-04	WH-BOM-01	ITM-HDD-01	0	3	36	f	none	simulated	system_sim
9380	2026-08-04	WH-BOM-01	ITM-CHG-01	0	8	177	f	none	simulated	system_sim
9381	2026-08-04	WH-BOM-01	ITM-CBL-01	0	4	184	f	none	simulated	system_sim
9382	2026-08-04	WH-DEL-01	ITM-CPU-01	0	2	62	f	none	simulated	system_sim
9383	2026-08-04	WH-DEL-01	ITM-GPU-01	0	0	18	f	none	simulated	system_sim
9384	2026-08-04	WH-DEL-01	ITM-RAM-01	75	8	98	f	none	simulated	system_sim
9385	2026-08-04	WH-DEL-01	ITM-SSD-01	0	1	60	f	none	simulated	system_sim
9386	2026-08-04	WH-DEL-01	ITM-HDD-01	0	3	30	f	none	simulated	system_sim
9387	2026-08-04	WH-DEL-01	ITM-CHG-01	0	5	185	f	none	simulated	system_sim
9388	2026-08-04	WH-DEL-01	ITM-CBL-01	0	9	178	f	none	simulated	system_sim
9389	2026-08-04	WH-CCU-01	ITM-CPU-01	0	0	26	f	none	simulated	system_sim
9390	2026-08-04	WH-CCU-01	ITM-GPU-01	0	0	18	f	none	simulated	system_sim
9391	2026-08-04	WH-CCU-01	ITM-RAM-01	0	8	91	f	none	simulated	system_sim
9392	2026-08-04	WH-CCU-01	ITM-SSD-01	0	0	56	f	none	simulated	system_sim
9393	2026-08-04	WH-CCU-01	ITM-HDD-01	0	0	32	f	none	simulated	system_sim
9394	2026-08-04	WH-CCU-01	ITM-CHG-01	0	1	183	f	none	simulated	system_sim
9395	2026-08-04	WH-CCU-01	ITM-CBL-01	0	8	166	f	none	simulated	system_sim
9396	2026-08-05	WH-BLR-01	ITM-CPU-01	0	1	22	f	none	simulated	system_sim
9397	2026-08-05	WH-BLR-01	ITM-GPU-01	0	1	6	t	shrinkage	simulated	system_sim
9398	2026-08-05	WH-BLR-01	ITM-RAM-01	0	4	103	f	none	simulated	system_sim
9399	2026-08-05	WH-BLR-01	ITM-SSD-01	0	1	59	f	none	simulated	system_sim
9400	2026-08-05	WH-BLR-01	ITM-HDD-01	0	0	34	f	none	simulated	system_sim
9401	2026-08-05	WH-BLR-01	ITM-CHG-01	0	3	187	f	none	simulated	system_sim
9402	2026-08-05	WH-BLR-01	ITM-CBL-01	0	5	151	f	none	simulated	system_sim
9403	2026-08-05	WH-CHN-01	ITM-CPU-01	0	1	45	f	none	simulated	system_sim
9404	2026-08-05	WH-CHN-01	ITM-GPU-01	0	2	21	f	none	simulated	system_sim
9405	2026-08-05	WH-CHN-01	ITM-RAM-01	0	8	92	f	none	simulated	system_sim
9406	2026-08-05	WH-CHN-01	ITM-SSD-01	0	0	64	f	none	simulated	system_sim
9407	2026-08-05	WH-CHN-01	ITM-HDD-01	0	1	84	f	none	simulated	system_sim
9408	2026-08-05	WH-CHN-01	ITM-CHG-01	0	1	185	f	none	simulated	system_sim
9409	2026-08-05	WH-CHN-01	ITM-CBL-01	0	5	162	f	none	simulated	system_sim
9410	2026-08-05	WH-BOM-01	ITM-CPU-01	0	3	62	f	none	simulated	system_sim
9411	2026-08-05	WH-BOM-01	ITM-GPU-01	0	1	42	f	none	simulated	system_sim
9412	2026-08-05	WH-BOM-01	ITM-RAM-01	0	9	57	f	none	simulated	system_sim
9413	2026-08-05	WH-BOM-01	ITM-SSD-01	0	0	64	f	none	simulated	system_sim
9414	2026-08-05	WH-BOM-01	ITM-HDD-01	0	2	34	f	none	simulated	system_sim
9415	2026-08-05	WH-BOM-01	ITM-CHG-01	0	9	168	f	none	simulated	system_sim
9416	2026-08-05	WH-BOM-01	ITM-CBL-01	0	8	176	f	none	simulated	system_sim
9417	2026-08-05	WH-DEL-01	ITM-CPU-01	0	2	60	f	none	simulated	system_sim
9418	2026-08-05	WH-DEL-01	ITM-GPU-01	0	0	18	f	none	simulated	system_sim
9419	2026-08-05	WH-DEL-01	ITM-RAM-01	0	4	94	f	none	simulated	system_sim
9420	2026-08-05	WH-DEL-01	ITM-SSD-01	0	1	59	f	none	simulated	system_sim
9421	2026-08-05	WH-DEL-01	ITM-HDD-01	0	2	28	f	none	simulated	system_sim
9422	2026-08-05	WH-DEL-01	ITM-CHG-01	0	8	177	f	none	simulated	system_sim
9423	2026-08-05	WH-DEL-01	ITM-CBL-01	0	1	177	f	none	simulated	system_sim
9424	2026-08-05	WH-CCU-01	ITM-CPU-01	0	0	26	f	none	simulated	system_sim
9425	2026-08-05	WH-CCU-01	ITM-GPU-01	0	2	16	f	none	simulated	system_sim
9426	2026-08-05	WH-CCU-01	ITM-RAM-01	0	7	84	f	none	simulated	system_sim
9427	2026-08-05	WH-CCU-01	ITM-SSD-01	0	2	54	f	none	simulated	system_sim
9428	2026-08-05	WH-CCU-01	ITM-HDD-01	0	0	32	f	none	simulated	system_sim
9429	2026-08-05	WH-CCU-01	ITM-CHG-01	0	7	176	f	none	simulated	system_sim
9430	2026-08-05	WH-CCU-01	ITM-CBL-01	0	10	156	f	none	simulated	system_sim
9431	2026-08-06	WH-BLR-01	ITM-CPU-01	45	2	65	f	none	simulated	system_sim
9432	2026-08-06	WH-BLR-01	ITM-GPU-01	30	2	34	f	none	simulated	system_sim
9433	2026-08-06	WH-BLR-01	ITM-RAM-01	0	10	93	f	none	simulated	system_sim
9434	2026-08-06	WH-BLR-01	ITM-SSD-01	0	0	59	f	none	simulated	system_sim
9435	2026-08-06	WH-BLR-01	ITM-HDD-01	0	2	32	f	none	simulated	system_sim
9436	2026-08-06	WH-BLR-01	ITM-CHG-01	0	3	184	f	none	simulated	system_sim
9437	2026-08-06	WH-BLR-01	ITM-CBL-01	0	8	143	f	none	simulated	system_sim
9438	2026-08-06	WH-CHN-01	ITM-CPU-01	0	0	45	f	none	simulated	system_sim
9439	2026-08-06	WH-CHN-01	ITM-GPU-01	0	0	21	f	none	simulated	system_sim
9440	2026-08-06	WH-CHN-01	ITM-RAM-01	0	9	83	f	none	simulated	system_sim
9441	2026-08-06	WH-CHN-01	ITM-SSD-01	0	3	61	f	none	simulated	system_sim
9442	2026-08-06	WH-CHN-01	ITM-HDD-01	0	2	82	f	none	simulated	system_sim
9443	2026-08-06	WH-CHN-01	ITM-CHG-01	0	1	184	f	none	simulated	system_sim
9444	2026-08-06	WH-CHN-01	ITM-CBL-01	0	3	159	f	none	simulated	system_sim
9445	2026-08-06	WH-BOM-01	ITM-CPU-01	0	3	59	f	none	simulated	system_sim
9446	2026-08-06	WH-BOM-01	ITM-GPU-01	0	0	42	f	none	simulated	system_sim
9447	2026-08-06	WH-BOM-01	ITM-RAM-01	0	2	55	f	none	simulated	system_sim
9448	2026-08-06	WH-BOM-01	ITM-SSD-01	0	3	61	f	none	simulated	system_sim
9449	2026-08-06	WH-BOM-01	ITM-HDD-01	0	1	33	f	none	simulated	system_sim
9450	2026-08-06	WH-BOM-01	ITM-CHG-01	0	10	158	f	none	simulated	system_sim
9451	2026-08-06	WH-BOM-01	ITM-CBL-01	0	5	171	f	none	simulated	system_sim
9452	2026-08-06	WH-DEL-01	ITM-CPU-01	0	0	60	f	none	simulated	system_sim
9453	2026-08-06	WH-DEL-01	ITM-GPU-01	0	0	18	f	none	simulated	system_sim
9454	2026-08-06	WH-DEL-01	ITM-RAM-01	0	8	86	f	none	simulated	system_sim
9455	2026-08-06	WH-DEL-01	ITM-SSD-01	0	3	56	f	none	simulated	system_sim
9456	2026-08-06	WH-DEL-01	ITM-HDD-01	60	3	85	f	none	simulated	system_sim
9457	2026-08-06	WH-DEL-01	ITM-CHG-01	0	9	168	f	none	simulated	system_sim
9458	2026-08-06	WH-DEL-01	ITM-CBL-01	0	9	168	f	none	simulated	system_sim
9459	2026-08-06	WH-CCU-01	ITM-CPU-01	0	3	23	f	none	simulated	system_sim
9460	2026-08-06	WH-CCU-01	ITM-GPU-01	0	0	16	f	none	simulated	system_sim
9461	2026-08-06	WH-CCU-01	ITM-RAM-01	0	4	80	f	none	simulated	system_sim
9462	2026-08-06	WH-CCU-01	ITM-SSD-01	0	1	53	f	none	simulated	system_sim
9463	2026-08-06	WH-CCU-01	ITM-HDD-01	0	0	32	f	none	simulated	system_sim
9464	2026-08-06	WH-CCU-01	ITM-CHG-01	0	5	171	f	none	simulated	system_sim
9465	2026-08-06	WH-CCU-01	ITM-CBL-01	0	1	155	f	none	simulated	system_sim
9466	2026-08-07	WH-BLR-01	ITM-CPU-01	0	2	63	f	none	simulated	system_sim
9467	2026-08-07	WH-BLR-01	ITM-GPU-01	0	0	34	f	none	simulated	system_sim
9468	2026-08-07	WH-BLR-01	ITM-RAM-01	0	7	86	f	none	simulated	system_sim
9469	2026-08-07	WH-BLR-01	ITM-SSD-01	0	2	57	f	none	simulated	system_sim
9470	2026-08-07	WH-BLR-01	ITM-HDD-01	0	2	30	f	none	simulated	system_sim
9471	2026-08-07	WH-BLR-01	ITM-CHG-01	0	10	174	f	none	simulated	system_sim
9472	2026-08-07	WH-BLR-01	ITM-CBL-01	300	3	440	f	none	simulated	system_sim
9473	2026-08-07	WH-CHN-01	ITM-CPU-01	0	1	44	f	none	simulated	system_sim
9474	2026-08-07	WH-CHN-01	ITM-GPU-01	0	0	21	f	none	simulated	system_sim
9475	2026-08-07	WH-CHN-01	ITM-RAM-01	0	7	76	f	none	simulated	system_sim
9476	2026-08-07	WH-CHN-01	ITM-SSD-01	0	3	58	f	none	simulated	system_sim
9477	2026-08-07	WH-CHN-01	ITM-HDD-01	0	3	79	f	none	simulated	system_sim
9478	2026-08-07	WH-CHN-01	ITM-CHG-01	0	6	178	f	none	simulated	system_sim
9479	2026-08-07	WH-CHN-01	ITM-CBL-01	0	9	150	f	none	simulated	system_sim
9480	2026-08-07	WH-BOM-01	ITM-CPU-01	0	0	59	f	none	simulated	system_sim
9481	2026-08-07	WH-BOM-01	ITM-GPU-01	0	0	42	f	none	simulated	system_sim
9482	2026-08-07	WH-BOM-01	ITM-RAM-01	0	9	46	f	none	simulated	system_sim
9483	2026-08-07	WH-BOM-01	ITM-SSD-01	0	1	60	f	none	simulated	system_sim
9484	2026-08-07	WH-BOM-01	ITM-HDD-01	0	2	31	f	none	simulated	system_sim
9485	2026-08-07	WH-BOM-01	ITM-CHG-01	0	5	153	f	none	simulated	system_sim
9486	2026-08-07	WH-BOM-01	ITM-CBL-01	0	2	169	f	none	simulated	system_sim
9487	2026-08-07	WH-DEL-01	ITM-CPU-01	0	1	59	f	none	simulated	system_sim
9488	2026-08-07	WH-DEL-01	ITM-GPU-01	0	2	16	f	none	simulated	system_sim
9489	2026-08-07	WH-DEL-01	ITM-RAM-01	0	9	77	f	none	simulated	system_sim
9490	2026-08-07	WH-DEL-01	ITM-SSD-01	0	0	56	f	none	simulated	system_sim
9491	2026-08-07	WH-DEL-01	ITM-HDD-01	0	1	84	f	none	simulated	system_sim
9492	2026-08-07	WH-DEL-01	ITM-CHG-01	0	4	164	f	none	simulated	system_sim
9493	2026-08-07	WH-DEL-01	ITM-CBL-01	0	2	166	f	none	simulated	system_sim
9494	2026-08-07	WH-CCU-01	ITM-CPU-01	0	3	20	f	none	simulated	system_sim
9495	2026-08-07	WH-CCU-01	ITM-GPU-01	0	0	16	f	none	simulated	system_sim
9496	2026-08-07	WH-CCU-01	ITM-RAM-01	0	5	75	f	none	simulated	system_sim
9497	2026-08-07	WH-CCU-01	ITM-SSD-01	0	0	53	f	none	simulated	system_sim
9498	2026-08-07	WH-CCU-01	ITM-HDD-01	0	0	32	f	none	simulated	system_sim
9499	2026-08-07	WH-CCU-01	ITM-CHG-01	0	6	165	f	none	simulated	system_sim
9500	2026-08-07	WH-CCU-01	ITM-CBL-01	0	10	145	f	none	simulated	system_sim
9501	2026-08-08	WH-BLR-01	ITM-CPU-01	0	0	63	f	none	simulated	system_sim
9502	2026-08-08	WH-BLR-01	ITM-GPU-01	0	0	34	f	none	simulated	system_sim
9503	2026-08-08	WH-BLR-01	ITM-RAM-01	0	1	85	f	none	simulated	system_sim
9504	2026-08-08	WH-BLR-01	ITM-SSD-01	0	0	57	f	none	simulated	system_sim
9505	2026-08-08	WH-BLR-01	ITM-HDD-01	0	1	29	f	none	simulated	system_sim
9506	2026-08-08	WH-BLR-01	ITM-CHG-01	0	6	168	f	none	simulated	system_sim
9507	2026-08-08	WH-BLR-01	ITM-CBL-01	0	2	438	f	none	simulated	system_sim
9508	2026-08-08	WH-CHN-01	ITM-CPU-01	0	3	41	f	none	simulated	system_sim
9509	2026-08-08	WH-CHN-01	ITM-GPU-01	0	1	20	f	none	simulated	system_sim
9510	2026-08-08	WH-CHN-01	ITM-RAM-01	0	7	69	f	none	simulated	system_sim
9511	2026-08-08	WH-CHN-01	ITM-SSD-01	0	1	57	f	none	simulated	system_sim
9512	2026-08-08	WH-CHN-01	ITM-HDD-01	0	3	76	f	none	simulated	system_sim
9513	2026-08-08	WH-CHN-01	ITM-CHG-01	0	9	169	f	none	simulated	system_sim
9514	2026-08-08	WH-CHN-01	ITM-CBL-01	0	7	143	f	none	simulated	system_sim
9515	2026-08-08	WH-BOM-01	ITM-CPU-01	0	2	57	f	none	simulated	system_sim
9516	2026-08-08	WH-BOM-01	ITM-GPU-01	0	0	42	f	none	simulated	system_sim
9517	2026-08-08	WH-BOM-01	ITM-RAM-01	0	2	44	f	none	simulated	system_sim
9518	2026-08-08	WH-BOM-01	ITM-SSD-01	0	3	57	f	none	simulated	system_sim
9519	2026-08-08	WH-BOM-01	ITM-HDD-01	0	2	29	f	none	simulated	system_sim
9520	2026-08-08	WH-BOM-01	ITM-CHG-01	0	10	143	f	none	simulated	system_sim
9521	2026-08-08	WH-BOM-01	ITM-CBL-01	0	7	162	f	none	simulated	system_sim
9522	2026-08-08	WH-DEL-01	ITM-CPU-01	0	3	56	f	none	simulated	system_sim
9523	2026-08-08	WH-DEL-01	ITM-GPU-01	0	2	14	f	none	simulated	system_sim
9524	2026-08-08	WH-DEL-01	ITM-RAM-01	0	10	67	f	none	simulated	system_sim
9525	2026-08-08	WH-DEL-01	ITM-SSD-01	0	2	54	f	none	simulated	system_sim
9526	2026-08-08	WH-DEL-01	ITM-HDD-01	0	0	84	f	none	simulated	system_sim
9527	2026-08-08	WH-DEL-01	ITM-CHG-01	0	7	157	f	none	simulated	system_sim
9528	2026-08-08	WH-DEL-01	ITM-CBL-01	0	3	163	f	none	simulated	system_sim
9529	2026-08-08	WH-CCU-01	ITM-CPU-01	45	0	65	f	none	simulated	system_sim
9530	2026-08-08	WH-CCU-01	ITM-GPU-01	0	1	15	f	none	simulated	system_sim
9531	2026-08-08	WH-CCU-01	ITM-RAM-01	0	7	68	f	none	simulated	system_sim
9532	2026-08-08	WH-CCU-01	ITM-SSD-01	0	3	50	f	none	simulated	system_sim
9533	2026-08-08	WH-CCU-01	ITM-HDD-01	0	3	29	f	none	simulated	system_sim
9534	2026-08-08	WH-CCU-01	ITM-CHG-01	0	10	155	f	none	simulated	system_sim
9535	2026-08-08	WH-CCU-01	ITM-CBL-01	300	6	439	f	none	simulated	system_sim
9536	2026-08-09	WH-BLR-01	ITM-CPU-01	0	1	62	f	none	simulated	system_sim
9537	2026-08-09	WH-BLR-01	ITM-GPU-01	0	0	34	f	none	simulated	system_sim
9538	2026-08-09	WH-BLR-01	ITM-RAM-01	0	5	80	f	none	simulated	system_sim
9539	2026-08-09	WH-BLR-01	ITM-SSD-01	0	0	57	f	none	simulated	system_sim
9540	2026-08-09	WH-BLR-01	ITM-HDD-01	60	0	89	f	none	simulated	system_sim
9541	2026-08-09	WH-BLR-01	ITM-CHG-01	0	9	159	f	none	simulated	system_sim
9542	2026-08-09	WH-BLR-01	ITM-CBL-01	0	6	432	f	none	simulated	system_sim
9543	2026-08-09	WH-CHN-01	ITM-CPU-01	0	2	39	f	none	simulated	system_sim
9544	2026-08-09	WH-CHN-01	ITM-GPU-01	0	0	20	f	none	simulated	system_sim
9545	2026-08-09	WH-CHN-01	ITM-RAM-01	0	10	59	f	none	simulated	system_sim
9546	2026-08-09	WH-CHN-01	ITM-SSD-01	0	0	57	f	none	simulated	system_sim
9547	2026-08-09	WH-CHN-01	ITM-HDD-01	0	1	75	f	none	simulated	system_sim
9548	2026-08-09	WH-CHN-01	ITM-CHG-01	0	8	161	f	none	simulated	system_sim
9549	2026-08-09	WH-CHN-01	ITM-CBL-01	300	2	441	f	none	simulated	system_sim
9550	2026-08-09	WH-BOM-01	ITM-CPU-01	0	3	54	f	none	simulated	system_sim
9551	2026-08-09	WH-BOM-01	ITM-GPU-01	0	0	42	f	none	simulated	system_sim
9552	2026-08-09	WH-BOM-01	ITM-RAM-01	0	6	38	f	none	simulated	system_sim
9553	2026-08-09	WH-BOM-01	ITM-SSD-01	0	3	54	f	none	simulated	system_sim
9554	2026-08-09	WH-BOM-01	ITM-HDD-01	60	1	88	f	none	simulated	system_sim
9555	2026-08-09	WH-BOM-01	ITM-CHG-01	0	5	138	f	none	simulated	system_sim
9556	2026-08-09	WH-BOM-01	ITM-CBL-01	0	7	155	f	none	simulated	system_sim
9557	2026-08-09	WH-DEL-01	ITM-CPU-01	0	0	56	f	none	simulated	system_sim
9558	2026-08-09	WH-DEL-01	ITM-GPU-01	30	0	44	f	none	simulated	system_sim
9559	2026-08-09	WH-DEL-01	ITM-RAM-01	0	5	62	f	none	simulated	system_sim
9560	2026-08-09	WH-DEL-01	ITM-SSD-01	0	0	54	f	none	simulated	system_sim
9561	2026-08-09	WH-DEL-01	ITM-HDD-01	0	3	81	f	none	simulated	system_sim
9562	2026-08-09	WH-DEL-01	ITM-CHG-01	0	1	156	f	none	simulated	system_sim
9563	2026-08-09	WH-DEL-01	ITM-CBL-01	0	6	157	f	none	simulated	system_sim
9564	2026-08-09	WH-CCU-01	ITM-CPU-01	0	0	65	f	none	simulated	system_sim
9565	2026-08-09	WH-CCU-01	ITM-GPU-01	0	2	13	f	none	simulated	system_sim
9566	2026-08-09	WH-CCU-01	ITM-RAM-01	0	5	63	f	none	simulated	system_sim
9567	2026-08-09	WH-CCU-01	ITM-SSD-01	0	0	50	f	none	simulated	system_sim
9568	2026-08-09	WH-CCU-01	ITM-HDD-01	60	1	88	f	none	simulated	system_sim
9569	2026-08-09	WH-CCU-01	ITM-CHG-01	0	2	153	f	none	simulated	system_sim
9570	2026-08-09	WH-CCU-01	ITM-CBL-01	0	3	436	f	none	simulated	system_sim
9571	2026-08-10	WH-BLR-01	ITM-CPU-01	0	3	59	f	none	simulated	system_sim
9572	2026-08-10	WH-BLR-01	ITM-GPU-01	0	1	33	f	none	simulated	system_sim
9573	2026-08-10	WH-BLR-01	ITM-RAM-01	0	5	75	f	none	simulated	system_sim
9574	2026-08-10	WH-BLR-01	ITM-SSD-01	0	3	54	f	none	simulated	system_sim
9575	2026-08-10	WH-BLR-01	ITM-HDD-01	0	0	89	f	none	simulated	system_sim
9576	2026-08-10	WH-BLR-01	ITM-CHG-01	0	1	158	f	none	simulated	system_sim
9577	2026-08-10	WH-BLR-01	ITM-CBL-01	0	2	430	f	none	simulated	system_sim
9578	2026-08-10	WH-CHN-01	ITM-CPU-01	0	3	36	f	none	simulated	system_sim
9579	2026-08-10	WH-CHN-01	ITM-GPU-01	0	0	20	f	none	simulated	system_sim
9580	2026-08-10	WH-CHN-01	ITM-RAM-01	0	7	52	f	none	simulated	system_sim
9581	2026-08-10	WH-CHN-01	ITM-SSD-01	0	1	56	f	none	simulated	system_sim
9582	2026-08-10	WH-CHN-01	ITM-HDD-01	0	2	73	f	none	simulated	system_sim
9583	2026-08-10	WH-CHN-01	ITM-CHG-01	0	8	153	f	none	simulated	system_sim
9584	2026-08-10	WH-CHN-01	ITM-CBL-01	0	6	435	f	none	simulated	system_sim
9585	2026-08-10	WH-BOM-01	ITM-CPU-01	0	2	52	f	none	simulated	system_sim
9586	2026-08-10	WH-BOM-01	ITM-GPU-01	0	0	42	f	none	simulated	system_sim
9587	2026-08-10	WH-BOM-01	ITM-RAM-01	0	4	34	f	none	simulated	system_sim
9588	2026-08-10	WH-BOM-01	ITM-SSD-01	0	3	51	f	none	simulated	system_sim
9589	2026-08-10	WH-BOM-01	ITM-HDD-01	0	3	85	f	none	simulated	system_sim
9590	2026-08-10	WH-BOM-01	ITM-CHG-01	0	1	137	f	none	simulated	system_sim
9591	2026-08-10	WH-BOM-01	ITM-CBL-01	0	6	149	f	none	simulated	system_sim
9592	2026-08-10	WH-DEL-01	ITM-CPU-01	0	3	53	f	none	simulated	system_sim
9593	2026-08-10	WH-DEL-01	ITM-GPU-01	0	0	44	f	none	simulated	system_sim
9594	2026-08-10	WH-DEL-01	ITM-RAM-01	0	9	53	f	none	simulated	system_sim
9595	2026-08-10	WH-DEL-01	ITM-SSD-01	0	3	51	f	none	simulated	system_sim
9596	2026-08-10	WH-DEL-01	ITM-HDD-01	0	0	81	f	none	simulated	system_sim
9597	2026-08-10	WH-DEL-01	ITM-CHG-01	0	10	146	f	none	simulated	system_sim
9598	2026-08-10	WH-DEL-01	ITM-CBL-01	0	6	151	f	none	simulated	system_sim
9599	2026-08-10	WH-CCU-01	ITM-CPU-01	0	3	62	f	none	simulated	system_sim
9600	2026-08-10	WH-CCU-01	ITM-GPU-01	30	2	41	f	none	simulated	system_sim
9601	2026-08-10	WH-CCU-01	ITM-RAM-01	0	5	58	f	none	simulated	system_sim
9602	2026-08-10	WH-CCU-01	ITM-SSD-01	0	1	49	f	none	simulated	system_sim
9603	2026-08-10	WH-CCU-01	ITM-HDD-01	0	3	85	f	none	simulated	system_sim
9604	2026-08-10	WH-CCU-01	ITM-CHG-01	0	9	144	f	none	simulated	system_sim
9605	2026-08-10	WH-CCU-01	ITM-CBL-01	0	1	435	f	none	simulated	system_sim
9606	2026-08-11	WH-BLR-01	ITM-CPU-01	0	0	59	f	none	simulated	system_sim
9607	2026-08-11	WH-BLR-01	ITM-GPU-01	0	0	33	f	none	simulated	system_sim
9608	2026-08-11	WH-BLR-01	ITM-RAM-01	0	7	68	f	none	simulated	system_sim
9609	2026-08-11	WH-BLR-01	ITM-SSD-01	0	3	51	f	none	simulated	system_sim
9610	2026-08-11	WH-BLR-01	ITM-HDD-01	0	0	89	f	none	simulated	system_sim
9611	2026-08-11	WH-BLR-01	ITM-CHG-01	0	3	155	f	none	simulated	system_sim
9612	2026-08-11	WH-BLR-01	ITM-CBL-01	0	8	422	f	none	simulated	system_sim
9613	2026-08-11	WH-CHN-01	ITM-CPU-01	0	0	36	f	none	simulated	system_sim
9614	2026-08-11	WH-CHN-01	ITM-GPU-01	0	1	19	f	none	simulated	system_sim
9615	2026-08-11	WH-CHN-01	ITM-RAM-01	0	6	46	f	none	simulated	system_sim
9616	2026-08-11	WH-CHN-01	ITM-SSD-01	0	2	54	f	none	simulated	system_sim
9617	2026-08-11	WH-CHN-01	ITM-HDD-01	0	2	71	f	none	simulated	system_sim
9618	2026-08-11	WH-CHN-01	ITM-CHG-01	0	7	146	f	none	simulated	system_sim
9619	2026-08-11	WH-CHN-01	ITM-CBL-01	0	5	430	f	none	simulated	system_sim
9620	2026-08-11	WH-BOM-01	ITM-CPU-01	0	1	51	f	none	simulated	system_sim
9621	2026-08-11	WH-BOM-01	ITM-GPU-01	0	0	42	f	none	simulated	system_sim
9622	2026-08-11	WH-BOM-01	ITM-RAM-01	75	2	107	f	none	simulated	system_sim
9623	2026-08-11	WH-BOM-01	ITM-SSD-01	0	0	51	f	none	simulated	system_sim
9624	2026-08-11	WH-BOM-01	ITM-HDD-01	0	3	82	f	none	simulated	system_sim
9625	2026-08-11	WH-BOM-01	ITM-CHG-01	0	2	135	f	none	simulated	system_sim
9626	2026-08-11	WH-BOM-01	ITM-CBL-01	300	3	446	f	none	simulated	system_sim
9627	2026-08-11	WH-DEL-01	ITM-CPU-01	0	0	53	f	none	simulated	system_sim
9628	2026-08-11	WH-DEL-01	ITM-GPU-01	0	0	44	f	none	simulated	system_sim
9629	2026-08-11	WH-DEL-01	ITM-RAM-01	0	3	50	f	none	simulated	system_sim
9630	2026-08-11	WH-DEL-01	ITM-SSD-01	0	0	51	f	none	simulated	system_sim
9631	2026-08-11	WH-DEL-01	ITM-HDD-01	0	3	78	f	none	simulated	system_sim
9632	2026-08-11	WH-DEL-01	ITM-CHG-01	0	4	142	f	none	simulated	system_sim
9633	2026-08-11	WH-DEL-01	ITM-CBL-01	0	8	143	f	none	simulated	system_sim
9634	2026-08-11	WH-CCU-01	ITM-CPU-01	0	0	62	f	none	simulated	system_sim
9635	2026-08-11	WH-CCU-01	ITM-GPU-01	0	1	40	f	none	simulated	system_sim
9636	2026-08-11	WH-CCU-01	ITM-RAM-01	0	6	52	f	none	simulated	system_sim
9637	2026-08-11	WH-CCU-01	ITM-SSD-01	0	2	47	f	none	simulated	system_sim
9638	2026-08-11	WH-CCU-01	ITM-HDD-01	0	0	85	f	none	simulated	system_sim
9639	2026-08-11	WH-CCU-01	ITM-CHG-01	0	6	138	f	none	simulated	system_sim
9640	2026-08-11	WH-CCU-01	ITM-CBL-01	0	7	428	f	none	simulated	system_sim
\.


--
-- Data for Name: system_health_snapshots; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_health_snapshots (id, service, status, latency_ms, "timestamp") FROM stdin;
1	database	HEALTHY	0	2026-08-19 15:43:16.958992
2	redis	NOT_CONFIGURED	\N	2026-08-19 15:43:16.958992
3	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:43:16.958992
4	celery	NOT_CONFIGURED	\N	2026-08-19 15:43:16.958992
5	email	HEALTHY	\N	2026-08-19 15:43:16.958992
6	backup	DEGRADED	\N	2026-08-19 15:43:16.960009
7	sentry	NOT_CONFIGURED	\N	2026-08-19 15:43:16.960009
8	openai	NOT_CONFIGURED	\N	2026-08-19 15:43:16.960009
9	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:43:16.960009
10	simulation	HEALTHY	\N	2026-08-19 15:43:16.960009
11	application	HEALTHY	4.5	2026-08-19 15:43:16.960009
12	database	HEALTHY	5.94	2026-08-19 15:43:47.085618
13	redis	NOT_CONFIGURED	\N	2026-08-19 15:43:47.085618
14	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:43:47.086299
15	celery	NOT_CONFIGURED	\N	2026-08-19 15:43:47.086299
16	email	HEALTHY	\N	2026-08-19 15:43:47.086299
17	backup	DEGRADED	\N	2026-08-19 15:43:47.086299
18	sentry	NOT_CONFIGURED	\N	2026-08-19 15:43:47.086299
19	openai	NOT_CONFIGURED	\N	2026-08-19 15:43:47.086299
20	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:43:47.086299
21	simulation	HEALTHY	\N	2026-08-19 15:43:47.086299
22	application	HEALTHY	4.5	2026-08-19 15:43:47.086299
23	database	HEALTHY	3.02	2026-08-19 15:44:17.211859
24	redis	NOT_CONFIGURED	\N	2026-08-19 15:44:17.211859
25	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:44:17.211859
26	celery	NOT_CONFIGURED	\N	2026-08-19 15:44:17.211859
27	email	HEALTHY	\N	2026-08-19 15:44:17.211859
28	backup	DEGRADED	\N	2026-08-19 15:44:17.211859
29	sentry	NOT_CONFIGURED	\N	2026-08-19 15:44:17.211859
30	openai	NOT_CONFIGURED	\N	2026-08-19 15:44:17.212864
31	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:44:17.212864
32	simulation	HEALTHY	\N	2026-08-19 15:44:17.212864
33	application	HEALTHY	4.5	2026-08-19 15:44:17.212864
34	database	HEALTHY	5.99	2026-08-19 15:44:47.457941
35	redis	NOT_CONFIGURED	\N	2026-08-19 15:44:47.457941
36	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:44:47.458945
37	celery	NOT_CONFIGURED	\N	2026-08-19 15:44:47.458945
38	email	HEALTHY	\N	2026-08-19 15:44:47.458945
39	backup	DEGRADED	\N	2026-08-19 15:44:47.458945
40	sentry	NOT_CONFIGURED	\N	2026-08-19 15:44:47.458945
41	openai	NOT_CONFIGURED	\N	2026-08-19 15:44:47.458945
42	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:44:47.458945
43	simulation	HEALTHY	\N	2026-08-19 15:44:47.458945
44	application	HEALTHY	4.5	2026-08-19 15:44:47.458945
45	database	HEALTHY	3.71	2026-08-19 15:45:17.632382
46	redis	NOT_CONFIGURED	\N	2026-08-19 15:45:17.632382
47	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:45:17.632382
48	celery	NOT_CONFIGURED	\N	2026-08-19 15:45:17.632382
49	email	HEALTHY	\N	2026-08-19 15:45:17.632382
50	backup	DEGRADED	\N	2026-08-19 15:45:17.632382
51	sentry	NOT_CONFIGURED	\N	2026-08-19 15:45:17.632382
52	openai	NOT_CONFIGURED	\N	2026-08-19 15:45:17.632382
53	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:45:17.632382
54	simulation	HEALTHY	\N	2026-08-19 15:45:17.632382
55	application	HEALTHY	4.5	2026-08-19 15:45:17.632382
56	database	HEALTHY	1	2026-08-19 15:45:47.689904
57	redis	NOT_CONFIGURED	\N	2026-08-19 15:45:47.689904
58	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:45:47.689904
59	celery	NOT_CONFIGURED	\N	2026-08-19 15:45:47.689904
60	email	HEALTHY	\N	2026-08-19 15:45:47.689904
61	backup	DEGRADED	\N	2026-08-19 15:45:47.689904
62	sentry	NOT_CONFIGURED	\N	2026-08-19 15:45:47.689904
63	openai	NOT_CONFIGURED	\N	2026-08-19 15:45:47.689904
64	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:45:47.689904
65	simulation	HEALTHY	\N	2026-08-19 15:45:47.689904
66	application	HEALTHY	4.5	2026-08-19 15:45:47.689904
67	database	HEALTHY	1	2026-08-19 15:46:17.753805
68	redis	NOT_CONFIGURED	\N	2026-08-19 15:46:17.753805
69	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:46:17.753805
70	celery	NOT_CONFIGURED	\N	2026-08-19 15:46:17.753805
71	email	HEALTHY	\N	2026-08-19 15:46:17.753805
72	backup	DEGRADED	\N	2026-08-19 15:46:17.753805
73	sentry	NOT_CONFIGURED	\N	2026-08-19 15:46:17.753805
74	openai	NOT_CONFIGURED	\N	2026-08-19 15:46:17.753805
75	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:46:17.753805
76	simulation	HEALTHY	\N	2026-08-19 15:46:17.753805
77	application	HEALTHY	4.5	2026-08-19 15:46:17.753805
78	database	HEALTHY	1	2026-08-19 15:46:47.800965
79	redis	NOT_CONFIGURED	\N	2026-08-19 15:46:47.800965
80	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:46:47.800965
81	celery	NOT_CONFIGURED	\N	2026-08-19 15:46:47.800965
82	email	HEALTHY	\N	2026-08-19 15:46:47.80197
83	backup	DEGRADED	\N	2026-08-19 15:46:47.80197
84	sentry	NOT_CONFIGURED	\N	2026-08-19 15:46:47.80197
85	openai	NOT_CONFIGURED	\N	2026-08-19 15:46:47.80197
86	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:46:47.80197
87	simulation	HEALTHY	\N	2026-08-19 15:46:47.80197
88	application	HEALTHY	4.5	2026-08-19 15:46:47.80197
89	database	HEALTHY	0	2026-08-19 15:47:17.84018
90	redis	NOT_CONFIGURED	\N	2026-08-19 15:47:17.84018
91	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:47:17.84018
92	celery	NOT_CONFIGURED	\N	2026-08-19 15:47:17.84018
93	email	HEALTHY	\N	2026-08-19 15:47:17.84018
94	backup	DEGRADED	\N	2026-08-19 15:47:17.84018
95	sentry	NOT_CONFIGURED	\N	2026-08-19 15:47:17.84018
96	openai	NOT_CONFIGURED	\N	2026-08-19 15:47:17.84018
97	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:47:17.84018
98	simulation	HEALTHY	\N	2026-08-19 15:47:17.84018
99	application	HEALTHY	4.5	2026-08-19 15:47:17.84018
100	database	HEALTHY	0	2026-08-19 15:47:47.878138
101	redis	NOT_CONFIGURED	\N	2026-08-19 15:47:47.878138
102	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:47:47.878138
103	celery	NOT_CONFIGURED	\N	2026-08-19 15:47:47.878138
104	email	HEALTHY	\N	2026-08-19 15:47:47.878138
105	backup	DEGRADED	\N	2026-08-19 15:47:47.878138
106	sentry	NOT_CONFIGURED	\N	2026-08-19 15:47:47.878138
107	openai	NOT_CONFIGURED	\N	2026-08-19 15:47:47.879137
108	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:47:47.879137
109	simulation	HEALTHY	\N	2026-08-19 15:47:47.879137
110	application	HEALTHY	4.5	2026-08-19 15:47:47.879137
111	database	HEALTHY	0	2026-08-19 15:48:17.938924
112	redis	NOT_CONFIGURED	\N	2026-08-19 15:48:17.938924
113	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:48:17.938924
114	celery	NOT_CONFIGURED	\N	2026-08-19 15:48:17.938924
115	email	HEALTHY	\N	2026-08-19 15:48:17.938924
116	backup	DEGRADED	\N	2026-08-19 15:48:17.938924
117	sentry	NOT_CONFIGURED	\N	2026-08-19 15:48:17.938924
118	openai	NOT_CONFIGURED	\N	2026-08-19 15:48:17.938924
119	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:48:17.938924
120	simulation	HEALTHY	\N	2026-08-19 15:48:17.938924
121	application	HEALTHY	4.5	2026-08-19 15:48:17.938924
122	database	HEALTHY	0	2026-08-19 15:48:47.970409
123	redis	NOT_CONFIGURED	\N	2026-08-19 15:48:47.970409
124	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:48:47.970409
125	celery	NOT_CONFIGURED	\N	2026-08-19 15:48:47.970409
126	email	HEALTHY	\N	2026-08-19 15:48:47.970409
127	backup	DEGRADED	\N	2026-08-19 15:48:47.970409
128	sentry	NOT_CONFIGURED	\N	2026-08-19 15:48:47.970409
129	openai	NOT_CONFIGURED	\N	2026-08-19 15:48:47.970409
130	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:48:47.970409
131	simulation	HEALTHY	\N	2026-08-19 15:48:47.970409
132	application	HEALTHY	4.5	2026-08-19 15:48:47.970409
133	database	HEALTHY	0	2026-08-19 15:49:18.017824
134	redis	NOT_CONFIGURED	\N	2026-08-19 15:49:18.017824
135	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:49:18.017824
136	celery	NOT_CONFIGURED	\N	2026-08-19 15:49:18.017824
137	email	HEALTHY	\N	2026-08-19 15:49:18.017824
138	backup	DEGRADED	\N	2026-08-19 15:49:18.017824
139	sentry	NOT_CONFIGURED	\N	2026-08-19 15:49:18.017824
140	openai	NOT_CONFIGURED	\N	2026-08-19 15:49:18.017824
141	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:49:18.017824
142	simulation	HEALTHY	\N	2026-08-19 15:49:18.017824
143	application	HEALTHY	4.5	2026-08-19 15:49:18.017824
144	database	HEALTHY	0	2026-08-19 15:49:48.067227
145	redis	NOT_CONFIGURED	\N	2026-08-19 15:49:48.067227
146	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:49:48.067227
147	celery	NOT_CONFIGURED	\N	2026-08-19 15:49:48.067227
148	email	HEALTHY	\N	2026-08-19 15:49:48.067227
149	backup	DEGRADED	\N	2026-08-19 15:49:48.068228
150	sentry	NOT_CONFIGURED	\N	2026-08-19 15:49:48.068228
151	openai	NOT_CONFIGURED	\N	2026-08-19 15:49:48.068228
152	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:49:48.068228
153	simulation	HEALTHY	\N	2026-08-19 15:49:48.068228
154	application	HEALTHY	4.5	2026-08-19 15:49:48.068228
155	database	HEALTHY	0	2026-08-19 15:50:18.108276
156	redis	NOT_CONFIGURED	\N	2026-08-19 15:50:18.109288
157	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:50:18.109288
158	celery	NOT_CONFIGURED	\N	2026-08-19 15:50:18.109288
159	email	HEALTHY	\N	2026-08-19 15:50:18.109288
160	backup	DEGRADED	\N	2026-08-19 15:50:18.109288
161	sentry	NOT_CONFIGURED	\N	2026-08-19 15:50:18.109288
162	openai	NOT_CONFIGURED	\N	2026-08-19 15:50:18.109288
163	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:50:18.109288
164	simulation	HEALTHY	\N	2026-08-19 15:50:18.109288
165	application	HEALTHY	4.5	2026-08-19 15:50:18.109288
166	database	HEALTHY	0	2026-08-19 15:50:48.141889
167	redis	NOT_CONFIGURED	\N	2026-08-19 15:50:48.141889
168	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:50:48.141889
169	celery	NOT_CONFIGURED	\N	2026-08-19 15:50:48.141889
170	email	HEALTHY	\N	2026-08-19 15:50:48.141889
171	backup	DEGRADED	\N	2026-08-19 15:50:48.141889
172	sentry	NOT_CONFIGURED	\N	2026-08-19 15:50:48.143248
173	openai	NOT_CONFIGURED	\N	2026-08-19 15:50:48.143248
174	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:50:48.143248
175	simulation	HEALTHY	\N	2026-08-19 15:50:48.143248
176	application	HEALTHY	4.5	2026-08-19 15:50:48.143248
177	database	HEALTHY	0	2026-08-19 15:51:18.179254
178	redis	NOT_CONFIGURED	\N	2026-08-19 15:51:18.179254
179	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:51:18.179254
180	celery	NOT_CONFIGURED	\N	2026-08-19 15:51:18.180254
181	email	HEALTHY	\N	2026-08-19 15:51:18.180254
182	backup	DEGRADED	\N	2026-08-19 15:51:18.180254
183	sentry	NOT_CONFIGURED	\N	2026-08-19 15:51:18.180254
184	openai	NOT_CONFIGURED	\N	2026-08-19 15:51:18.180254
185	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:51:18.180254
186	simulation	HEALTHY	\N	2026-08-19 15:51:18.180254
187	application	HEALTHY	4.5	2026-08-19 15:51:18.180254
188	database	HEALTHY	0.69	2026-08-19 15:51:48.208362
189	redis	NOT_CONFIGURED	\N	2026-08-19 15:51:48.208362
190	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:51:48.208362
191	celery	NOT_CONFIGURED	\N	2026-08-19 15:51:48.208362
192	email	HEALTHY	\N	2026-08-19 15:51:48.208362
193	backup	DEGRADED	\N	2026-08-19 15:51:48.208362
194	sentry	NOT_CONFIGURED	\N	2026-08-19 15:51:48.208362
195	openai	NOT_CONFIGURED	\N	2026-08-19 15:51:48.208362
196	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:51:48.208362
197	simulation	HEALTHY	\N	2026-08-19 15:51:48.208362
198	application	HEALTHY	4.5	2026-08-19 15:51:48.208362
199	database	HEALTHY	1.02	2026-08-19 15:52:18.241292
200	redis	NOT_CONFIGURED	\N	2026-08-19 15:52:18.242297
201	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:52:18.242297
202	celery	NOT_CONFIGURED	\N	2026-08-19 15:52:18.242297
203	email	HEALTHY	\N	2026-08-19 15:52:18.242297
204	backup	DEGRADED	\N	2026-08-19 15:52:18.242297
205	sentry	NOT_CONFIGURED	\N	2026-08-19 15:52:18.242297
206	openai	NOT_CONFIGURED	\N	2026-08-19 15:52:18.242297
207	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:52:18.242297
208	simulation	HEALTHY	\N	2026-08-19 15:52:18.242297
209	application	HEALTHY	4.5	2026-08-19 15:52:18.242297
210	database	HEALTHY	1	2026-08-19 15:52:48.278019
211	redis	NOT_CONFIGURED	\N	2026-08-19 15:52:48.279014
212	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:52:48.279014
213	celery	NOT_CONFIGURED	\N	2026-08-19 15:52:48.279014
214	email	HEALTHY	\N	2026-08-19 15:52:48.279014
215	backup	DEGRADED	\N	2026-08-19 15:52:48.279014
216	sentry	NOT_CONFIGURED	\N	2026-08-19 15:52:48.279014
217	openai	NOT_CONFIGURED	\N	2026-08-19 15:52:48.279014
218	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:52:48.279014
219	simulation	HEALTHY	\N	2026-08-19 15:52:48.279014
220	application	HEALTHY	4.5	2026-08-19 15:52:48.279014
221	database	HEALTHY	1	2026-08-19 15:53:18.310184
222	redis	NOT_CONFIGURED	\N	2026-08-19 15:53:18.310184
223	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:53:18.310184
224	celery	NOT_CONFIGURED	\N	2026-08-19 15:53:18.310184
225	email	HEALTHY	\N	2026-08-19 15:53:18.310184
226	backup	DEGRADED	\N	2026-08-19 15:53:18.310184
227	sentry	NOT_CONFIGURED	\N	2026-08-19 15:53:18.310184
228	openai	NOT_CONFIGURED	\N	2026-08-19 15:53:18.310184
229	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:53:18.311185
230	simulation	HEALTHY	\N	2026-08-19 15:53:18.311185
231	application	HEALTHY	4.5	2026-08-19 15:53:18.311185
232	database	HEALTHY	1.05	2026-08-19 15:53:48.350893
233	redis	NOT_CONFIGURED	\N	2026-08-19 15:53:48.350893
234	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:53:48.350893
235	celery	NOT_CONFIGURED	\N	2026-08-19 15:53:48.350893
236	email	HEALTHY	\N	2026-08-19 15:53:48.350893
237	backup	DEGRADED	\N	2026-08-19 15:53:48.350893
238	sentry	NOT_CONFIGURED	\N	2026-08-19 15:53:48.350893
239	openai	NOT_CONFIGURED	\N	2026-08-19 15:53:48.350893
240	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:53:48.350893
241	simulation	HEALTHY	\N	2026-08-19 15:53:48.350893
242	application	HEALTHY	4.5	2026-08-19 15:53:48.350893
243	database	HEALTHY	0	2026-08-19 15:54:18.38665
244	redis	NOT_CONFIGURED	\N	2026-08-19 15:54:18.38665
245	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:54:18.38665
246	celery	NOT_CONFIGURED	\N	2026-08-19 15:54:18.38665
247	email	HEALTHY	\N	2026-08-19 15:54:18.38665
248	backup	DEGRADED	\N	2026-08-19 15:54:18.38665
249	sentry	NOT_CONFIGURED	\N	2026-08-19 15:54:18.38665
250	openai	NOT_CONFIGURED	\N	2026-08-19 15:54:18.38665
251	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:54:18.38665
252	simulation	HEALTHY	\N	2026-08-19 15:54:18.38665
253	application	HEALTHY	4.5	2026-08-19 15:54:18.38665
254	database	HEALTHY	0	2026-08-19 15:54:48.415246
255	redis	NOT_CONFIGURED	\N	2026-08-19 15:54:48.415246
256	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:54:48.415246
257	celery	NOT_CONFIGURED	\N	2026-08-19 15:54:48.415246
258	email	HEALTHY	\N	2026-08-19 15:54:48.415246
259	backup	DEGRADED	\N	2026-08-19 15:54:48.415246
260	sentry	NOT_CONFIGURED	\N	2026-08-19 15:54:48.415246
261	openai	NOT_CONFIGURED	\N	2026-08-19 15:54:48.415246
262	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:54:48.415246
263	simulation	HEALTHY	\N	2026-08-19 15:54:48.415246
264	application	HEALTHY	4.5	2026-08-19 15:54:48.415246
265	database	HEALTHY	1	2026-08-19 15:55:18.447024
266	redis	NOT_CONFIGURED	\N	2026-08-19 15:55:18.448023
267	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:55:18.448023
268	celery	NOT_CONFIGURED	\N	2026-08-19 15:55:18.448023
269	email	HEALTHY	\N	2026-08-19 15:55:18.448023
270	backup	DEGRADED	\N	2026-08-19 15:55:18.448023
271	sentry	NOT_CONFIGURED	\N	2026-08-19 15:55:18.448023
272	openai	NOT_CONFIGURED	\N	2026-08-19 15:55:18.448023
273	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:55:18.448023
274	simulation	HEALTHY	\N	2026-08-19 15:55:18.448023
275	application	HEALTHY	4.5	2026-08-19 15:55:18.448023
276	database	HEALTHY	0	2026-08-19 15:55:48.482337
277	redis	NOT_CONFIGURED	\N	2026-08-19 15:55:48.482337
278	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:55:48.482337
279	celery	NOT_CONFIGURED	\N	2026-08-19 15:55:48.482337
280	email	HEALTHY	\N	2026-08-19 15:55:48.482337
281	backup	DEGRADED	\N	2026-08-19 15:55:48.482337
282	sentry	NOT_CONFIGURED	\N	2026-08-19 15:55:48.482337
283	openai	NOT_CONFIGURED	\N	2026-08-19 15:55:48.482337
284	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:55:48.482337
285	simulation	HEALTHY	\N	2026-08-19 15:55:48.482337
286	application	HEALTHY	4.5	2026-08-19 15:55:48.482337
287	database	HEALTHY	1.66	2026-08-19 15:56:18.648095
288	redis	NOT_CONFIGURED	\N	2026-08-19 15:56:18.648095
289	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:56:18.648095
290	celery	NOT_CONFIGURED	\N	2026-08-19 15:56:18.648095
291	email	HEALTHY	\N	2026-08-19 15:56:18.648095
292	backup	DEGRADED	\N	2026-08-19 15:56:18.648095
293	sentry	NOT_CONFIGURED	\N	2026-08-19 15:56:18.648095
294	openai	NOT_CONFIGURED	\N	2026-08-19 15:56:18.648095
295	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:56:18.648095
296	simulation	HEALTHY	\N	2026-08-19 15:56:18.648095
297	application	HEALTHY	4.5	2026-08-19 15:56:18.648095
298	database	HEALTHY	0	2026-08-19 15:56:48.675899
299	redis	NOT_CONFIGURED	\N	2026-08-19 15:56:48.675899
300	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:56:48.675899
301	celery	NOT_CONFIGURED	\N	2026-08-19 15:56:48.675899
302	email	HEALTHY	\N	2026-08-19 15:56:48.675899
303	backup	DEGRADED	\N	2026-08-19 15:56:48.675899
304	sentry	NOT_CONFIGURED	\N	2026-08-19 15:56:48.675899
305	openai	NOT_CONFIGURED	\N	2026-08-19 15:56:48.675899
306	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:56:48.675899
307	simulation	HEALTHY	\N	2026-08-19 15:56:48.675899
308	application	HEALTHY	4.5	2026-08-19 15:56:48.675899
309	database	HEALTHY	0	2026-08-19 15:57:18.709025
310	redis	NOT_CONFIGURED	\N	2026-08-19 15:57:18.710392
311	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:57:18.710392
312	celery	NOT_CONFIGURED	\N	2026-08-19 15:57:18.710392
313	email	HEALTHY	\N	2026-08-19 15:57:18.710392
314	backup	DEGRADED	\N	2026-08-19 15:57:18.710392
315	sentry	NOT_CONFIGURED	\N	2026-08-19 15:57:18.710392
316	openai	NOT_CONFIGURED	\N	2026-08-19 15:57:18.710392
317	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:57:18.710392
318	simulation	HEALTHY	\N	2026-08-19 15:57:18.710392
319	application	HEALTHY	4.5	2026-08-19 15:57:18.710392
320	database	HEALTHY	0.51	2026-08-19 15:57:48.749251
321	redis	NOT_CONFIGURED	\N	2026-08-19 15:57:48.750811
322	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:57:48.750811
323	celery	NOT_CONFIGURED	\N	2026-08-19 15:57:48.750811
324	email	HEALTHY	\N	2026-08-19 15:57:48.750811
325	backup	DEGRADED	\N	2026-08-19 15:57:48.750811
326	sentry	NOT_CONFIGURED	\N	2026-08-19 15:57:48.750811
327	openai	NOT_CONFIGURED	\N	2026-08-19 15:57:48.750811
328	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:57:48.750811
329	simulation	HEALTHY	\N	2026-08-19 15:57:48.750811
330	application	HEALTHY	4.5	2026-08-19 15:57:48.750811
331	database	HEALTHY	0	2026-08-19 15:58:18.775742
332	redis	NOT_CONFIGURED	\N	2026-08-19 15:58:18.775742
333	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:58:18.775742
334	celery	NOT_CONFIGURED	\N	2026-08-19 15:58:18.775742
335	email	HEALTHY	\N	2026-08-19 15:58:18.775742
336	backup	DEGRADED	\N	2026-08-19 15:58:18.775742
337	sentry	NOT_CONFIGURED	\N	2026-08-19 15:58:18.775742
338	openai	NOT_CONFIGURED	\N	2026-08-19 15:58:18.775742
339	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:58:18.775742
340	simulation	HEALTHY	\N	2026-08-19 15:58:18.775742
341	application	HEALTHY	4.5	2026-08-19 15:58:18.776745
342	database	HEALTHY	1	2026-08-19 15:58:48.839837
343	redis	NOT_CONFIGURED	\N	2026-08-19 15:58:48.839837
344	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:58:48.839837
345	celery	NOT_CONFIGURED	\N	2026-08-19 15:58:48.839837
346	email	HEALTHY	\N	2026-08-19 15:58:48.839837
347	backup	DEGRADED	\N	2026-08-19 15:58:48.839837
348	sentry	NOT_CONFIGURED	\N	2026-08-19 15:58:48.840835
349	openai	NOT_CONFIGURED	\N	2026-08-19 15:58:48.840835
350	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:58:48.840835
351	simulation	HEALTHY	\N	2026-08-19 15:58:48.840835
352	application	HEALTHY	4.5	2026-08-19 15:58:48.840835
353	database	HEALTHY	0	2026-08-19 15:59:18.887093
354	redis	NOT_CONFIGURED	\N	2026-08-19 15:59:18.887093
355	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:59:18.887093
356	celery	NOT_CONFIGURED	\N	2026-08-19 15:59:18.887093
357	email	HEALTHY	\N	2026-08-19 15:59:18.887093
358	backup	DEGRADED	\N	2026-08-19 15:59:18.887093
359	sentry	NOT_CONFIGURED	\N	2026-08-19 15:59:18.887093
360	openai	NOT_CONFIGURED	\N	2026-08-19 15:59:18.887093
361	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:59:18.887093
362	simulation	HEALTHY	\N	2026-08-19 15:59:18.887093
363	application	HEALTHY	4.5	2026-08-19 15:59:18.887093
364	database	HEALTHY	2	2026-08-19 15:59:48.921252
365	redis	NOT_CONFIGURED	\N	2026-08-19 15:59:48.922252
366	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:59:48.922252
367	celery	NOT_CONFIGURED	\N	2026-08-19 15:59:48.922252
368	email	HEALTHY	\N	2026-08-19 15:59:48.922252
369	backup	DEGRADED	\N	2026-08-19 15:59:48.922252
370	sentry	NOT_CONFIGURED	\N	2026-08-19 15:59:48.922252
371	openai	NOT_CONFIGURED	\N	2026-08-19 15:59:48.922252
372	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:59:48.922252
373	simulation	HEALTHY	\N	2026-08-19 15:59:48.922252
374	application	HEALTHY	4.5	2026-08-19 15:59:48.922252
375	database	HEALTHY	0.72	2026-08-19 16:00:18.986965
376	redis	NOT_CONFIGURED	\N	2026-08-19 16:00:18.986965
377	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:00:18.986965
378	celery	NOT_CONFIGURED	\N	2026-08-19 16:00:18.986965
379	email	HEALTHY	\N	2026-08-19 16:00:18.986965
380	backup	DEGRADED	\N	2026-08-19 16:00:18.986965
381	sentry	NOT_CONFIGURED	\N	2026-08-19 16:00:18.986965
382	openai	NOT_CONFIGURED	\N	2026-08-19 16:00:18.986965
383	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:00:18.986965
384	simulation	HEALTHY	\N	2026-08-19 16:00:18.986965
385	application	HEALTHY	4.5	2026-08-19 16:00:18.986965
386	database	HEALTHY	0	2026-08-19 16:00:49.058315
387	redis	NOT_CONFIGURED	\N	2026-08-19 16:00:49.058315
388	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:00:49.059309
389	celery	NOT_CONFIGURED	\N	2026-08-19 16:00:49.059309
390	email	HEALTHY	\N	2026-08-19 16:00:49.059309
391	backup	DEGRADED	\N	2026-08-19 16:00:49.059309
392	sentry	NOT_CONFIGURED	\N	2026-08-19 16:00:49.059309
393	openai	NOT_CONFIGURED	\N	2026-08-19 16:00:49.059309
394	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:00:49.059309
395	simulation	HEALTHY	\N	2026-08-19 16:00:49.059309
396	application	HEALTHY	4.5	2026-08-19 16:00:49.059309
397	database	HEALTHY	0.99	2026-08-19 16:01:19.090784
398	redis	NOT_CONFIGURED	\N	2026-08-19 16:01:19.090784
399	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:01:19.090784
400	celery	NOT_CONFIGURED	\N	2026-08-19 16:01:19.090784
401	email	HEALTHY	\N	2026-08-19 16:01:19.090784
402	backup	DEGRADED	\N	2026-08-19 16:01:19.090784
403	sentry	NOT_CONFIGURED	\N	2026-08-19 16:01:19.090784
404	openai	NOT_CONFIGURED	\N	2026-08-19 16:01:19.090784
405	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:01:19.090784
406	simulation	HEALTHY	\N	2026-08-19 16:01:19.090784
407	application	HEALTHY	4.5	2026-08-19 16:01:19.090784
408	database	HEALTHY	1	2026-08-19 16:01:49.238816
409	redis	NOT_CONFIGURED	\N	2026-08-19 16:01:49.238816
410	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:01:49.238816
411	celery	NOT_CONFIGURED	\N	2026-08-19 16:01:49.238816
412	email	HEALTHY	\N	2026-08-19 16:01:49.238816
413	backup	DEGRADED	\N	2026-08-19 16:01:49.238816
414	sentry	NOT_CONFIGURED	\N	2026-08-19 16:01:49.238816
415	openai	NOT_CONFIGURED	\N	2026-08-19 16:01:49.239799
416	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:01:49.239799
417	simulation	HEALTHY	\N	2026-08-19 16:01:49.239799
418	application	HEALTHY	4.5	2026-08-19 16:01:49.239799
419	database	HEALTHY	1	2026-08-19 16:02:19.277167
420	redis	NOT_CONFIGURED	\N	2026-08-19 16:02:19.277167
421	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:02:19.277167
422	celery	NOT_CONFIGURED	\N	2026-08-19 16:02:19.278171
423	email	HEALTHY	\N	2026-08-19 16:02:19.278171
424	backup	DEGRADED	\N	2026-08-19 16:02:19.278171
425	sentry	NOT_CONFIGURED	\N	2026-08-19 16:02:19.278171
426	openai	NOT_CONFIGURED	\N	2026-08-19 16:02:19.278171
427	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:02:19.278171
428	simulation	HEALTHY	\N	2026-08-19 16:02:19.278171
429	application	HEALTHY	4.5	2026-08-19 16:02:19.278171
430	database	HEALTHY	0	2026-08-19 16:02:49.309146
431	redis	NOT_CONFIGURED	\N	2026-08-19 16:02:49.309146
432	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:02:49.309146
433	celery	NOT_CONFIGURED	\N	2026-08-19 16:02:49.309146
434	email	HEALTHY	\N	2026-08-19 16:02:49.309146
435	backup	DEGRADED	\N	2026-08-19 16:02:49.309146
436	sentry	NOT_CONFIGURED	\N	2026-08-19 16:02:49.309146
437	openai	NOT_CONFIGURED	\N	2026-08-19 16:02:49.309146
438	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:02:49.309146
439	simulation	HEALTHY	\N	2026-08-19 16:02:49.309146
440	application	HEALTHY	4.5	2026-08-19 16:02:49.309146
441	database	HEALTHY	0	2026-08-19 16:03:19.347408
442	redis	NOT_CONFIGURED	\N	2026-08-19 16:03:19.348405
443	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:03:19.348405
444	celery	NOT_CONFIGURED	\N	2026-08-19 16:03:19.348405
445	email	HEALTHY	\N	2026-08-19 16:03:19.348405
446	backup	DEGRADED	\N	2026-08-19 16:03:19.348405
447	sentry	NOT_CONFIGURED	\N	2026-08-19 16:03:19.348405
448	openai	NOT_CONFIGURED	\N	2026-08-19 16:03:19.348405
449	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:03:19.348405
450	simulation	HEALTHY	\N	2026-08-19 16:03:19.348405
451	application	HEALTHY	4.5	2026-08-19 16:03:19.348405
452	database	HEALTHY	0	2026-08-19 16:03:49.394343
453	redis	NOT_CONFIGURED	\N	2026-08-19 16:03:49.394343
454	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:03:49.394343
455	celery	NOT_CONFIGURED	\N	2026-08-19 16:03:49.394343
456	email	HEALTHY	\N	2026-08-19 16:03:49.394343
457	backup	DEGRADED	\N	2026-08-19 16:03:49.394343
458	sentry	NOT_CONFIGURED	\N	2026-08-19 16:03:49.394343
459	openai	NOT_CONFIGURED	\N	2026-08-19 16:03:49.394343
460	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:03:49.394343
461	simulation	HEALTHY	\N	2026-08-19 16:03:49.394343
462	application	HEALTHY	4.5	2026-08-19 16:03:49.394343
463	database	HEALTHY	1	2026-08-19 16:04:19.434344
464	redis	NOT_CONFIGURED	\N	2026-08-19 16:04:19.43532
465	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:04:19.43532
466	celery	NOT_CONFIGURED	\N	2026-08-19 16:04:19.43532
467	email	HEALTHY	\N	2026-08-19 16:04:19.43532
468	backup	DEGRADED	\N	2026-08-19 16:04:19.43532
469	sentry	NOT_CONFIGURED	\N	2026-08-19 16:04:19.43532
470	openai	NOT_CONFIGURED	\N	2026-08-19 16:04:19.43532
471	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:04:19.43532
472	simulation	HEALTHY	\N	2026-08-19 16:04:19.43532
473	application	HEALTHY	4.5	2026-08-19 16:04:19.43532
474	database	HEALTHY	0	2026-08-19 16:04:49.498861
475	redis	NOT_CONFIGURED	\N	2026-08-19 16:04:49.498861
476	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:04:49.498861
477	celery	NOT_CONFIGURED	\N	2026-08-19 16:04:49.498861
478	email	HEALTHY	\N	2026-08-19 16:04:49.499858
479	backup	DEGRADED	\N	2026-08-19 16:04:49.499858
480	sentry	NOT_CONFIGURED	\N	2026-08-19 16:04:49.499858
481	openai	NOT_CONFIGURED	\N	2026-08-19 16:04:49.499858
482	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:04:49.499858
483	simulation	HEALTHY	\N	2026-08-19 16:04:49.499858
484	application	HEALTHY	4.5	2026-08-19 16:04:49.499858
485	database	HEALTHY	0	2026-08-19 16:05:19.529283
486	redis	NOT_CONFIGURED	\N	2026-08-19 16:05:19.529283
487	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:05:19.529283
488	celery	NOT_CONFIGURED	\N	2026-08-19 16:05:19.529283
489	email	HEALTHY	\N	2026-08-19 16:05:19.529283
490	backup	DEGRADED	\N	2026-08-19 16:05:19.529283
491	sentry	NOT_CONFIGURED	\N	2026-08-19 16:05:19.529283
492	openai	NOT_CONFIGURED	\N	2026-08-19 16:05:19.529283
493	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:05:19.529283
494	simulation	HEALTHY	\N	2026-08-19 16:05:19.529283
495	application	HEALTHY	4.5	2026-08-19 16:05:19.529283
496	database	HEALTHY	1	2026-08-19 16:05:49.581173
497	redis	NOT_CONFIGURED	\N	2026-08-19 16:05:49.581173
498	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:05:49.581173
499	celery	NOT_CONFIGURED	\N	2026-08-19 16:05:49.581173
500	email	HEALTHY	\N	2026-08-19 16:05:49.581173
501	backup	DEGRADED	\N	2026-08-19 16:05:49.581173
502	sentry	NOT_CONFIGURED	\N	2026-08-19 16:05:49.581173
503	openai	NOT_CONFIGURED	\N	2026-08-19 16:05:49.581173
504	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:05:49.581173
505	simulation	HEALTHY	\N	2026-08-19 16:05:49.581173
506	application	HEALTHY	4.5	2026-08-19 16:05:49.581173
507	database	HEALTHY	1	2026-08-19 16:06:19.623269
508	redis	NOT_CONFIGURED	\N	2026-08-19 16:06:19.623269
509	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:06:19.623269
510	celery	NOT_CONFIGURED	\N	2026-08-19 16:06:19.623269
511	email	HEALTHY	\N	2026-08-19 16:06:19.623269
512	backup	DEGRADED	\N	2026-08-19 16:06:19.623269
513	sentry	NOT_CONFIGURED	\N	2026-08-19 16:06:19.623269
514	openai	NOT_CONFIGURED	\N	2026-08-19 16:06:19.623269
515	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:06:19.623269
516	simulation	HEALTHY	\N	2026-08-19 16:06:19.623269
517	application	HEALTHY	4.5	2026-08-19 16:06:19.623269
518	database	HEALTHY	0	2026-08-19 16:06:49.655565
519	redis	NOT_CONFIGURED	\N	2026-08-19 16:06:49.656561
520	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:06:49.656561
521	celery	NOT_CONFIGURED	\N	2026-08-19 16:06:49.656561
522	email	HEALTHY	\N	2026-08-19 16:06:49.656561
523	backup	DEGRADED	\N	2026-08-19 16:06:49.656561
524	sentry	NOT_CONFIGURED	\N	2026-08-19 16:06:49.656561
525	openai	NOT_CONFIGURED	\N	2026-08-19 16:06:49.656561
526	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:06:49.656561
527	simulation	HEALTHY	\N	2026-08-19 16:06:49.656561
528	application	HEALTHY	4.5	2026-08-19 16:06:49.656561
529	database	HEALTHY	0	2026-08-19 16:07:19.686925
530	redis	NOT_CONFIGURED	\N	2026-08-19 16:07:19.687925
531	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:07:19.687925
532	celery	NOT_CONFIGURED	\N	2026-08-19 16:07:19.687925
533	email	HEALTHY	\N	2026-08-19 16:07:19.687925
534	backup	DEGRADED	\N	2026-08-19 16:07:19.687925
535	sentry	NOT_CONFIGURED	\N	2026-08-19 16:07:19.687925
536	openai	NOT_CONFIGURED	\N	2026-08-19 16:07:19.687925
537	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:07:19.687925
538	simulation	HEALTHY	\N	2026-08-19 16:07:19.687925
539	application	HEALTHY	4.5	2026-08-19 16:07:19.687925
540	database	HEALTHY	1	2026-08-19 16:07:49.742458
541	redis	NOT_CONFIGURED	\N	2026-08-19 16:07:49.743901
542	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:07:49.743901
543	celery	NOT_CONFIGURED	\N	2026-08-19 16:07:49.743901
544	email	HEALTHY	\N	2026-08-19 16:07:49.743901
545	backup	DEGRADED	\N	2026-08-19 16:07:49.743901
546	sentry	NOT_CONFIGURED	\N	2026-08-19 16:07:49.743901
547	openai	NOT_CONFIGURED	\N	2026-08-19 16:07:49.743901
548	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:07:49.743901
549	simulation	HEALTHY	\N	2026-08-19 16:07:49.743901
550	application	HEALTHY	4.5	2026-08-19 16:07:49.743901
551	database	HEALTHY	0	2026-08-19 16:08:19.773555
552	redis	NOT_CONFIGURED	\N	2026-08-19 16:08:19.773555
553	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:08:19.773555
554	celery	NOT_CONFIGURED	\N	2026-08-19 16:08:19.773555
555	email	HEALTHY	\N	2026-08-19 16:08:19.773555
556	backup	DEGRADED	\N	2026-08-19 16:08:19.773555
557	sentry	NOT_CONFIGURED	\N	2026-08-19 16:08:19.773555
558	openai	NOT_CONFIGURED	\N	2026-08-19 16:08:19.773555
559	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:08:19.773555
560	simulation	HEALTHY	\N	2026-08-19 16:08:19.773555
561	application	HEALTHY	4.5	2026-08-19 16:08:19.773555
1233	database	HEALTHY	1	2026-08-19 16:39:22.761803
1234	redis	NOT_CONFIGURED	\N	2026-08-19 16:39:22.761803
1235	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:39:22.761803
1236	celery	NOT_CONFIGURED	\N	2026-08-19 16:39:22.761803
1237	email	HEALTHY	\N	2026-08-19 16:39:22.761803
1238	backup	UNAVAILABLE	\N	2026-08-19 16:39:22.761803
1239	sentry	NOT_CONFIGURED	\N	2026-08-19 16:39:22.761803
1240	openai	NOT_CONFIGURED	\N	2026-08-19 16:39:22.761803
1241	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:39:22.761803
1242	simulation	HEALTHY	\N	2026-08-19 16:39:22.761803
1243	application	HEALTHY	4.5	2026-08-19 16:39:22.761803
1354	database	HEALTHY	8.02	2026-08-19 16:44:53.645413
1355	redis	NOT_CONFIGURED	\N	2026-08-19 16:44:53.646429
1356	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:44:53.646429
1357	celery	NOT_CONFIGURED	\N	2026-08-19 16:44:53.646429
1358	email	HEALTHY	\N	2026-08-19 16:44:53.646429
1359	backup	UNAVAILABLE	\N	2026-08-19 16:44:53.646429
1360	sentry	NOT_CONFIGURED	\N	2026-08-19 16:44:53.646429
1361	openai	NOT_CONFIGURED	\N	2026-08-19 16:44:53.646429
1362	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:44:53.64743
1363	simulation	HEALTHY	\N	2026-08-19 16:44:53.64743
1364	application	HEALTHY	4.5	2026-08-19 16:44:53.64743
1409	database	HEALTHY	1.01	2026-08-19 16:47:23.877649
1410	redis	NOT_CONFIGURED	\N	2026-08-19 16:47:23.877649
1411	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:47:23.877649
1412	celery	NOT_CONFIGURED	\N	2026-08-19 16:47:23.877649
1413	email	HEALTHY	\N	2026-08-19 16:47:23.877649
1414	backup	UNAVAILABLE	\N	2026-08-19 16:47:23.877649
1415	sentry	NOT_CONFIGURED	\N	2026-08-19 16:47:23.877649
1416	openai	NOT_CONFIGURED	\N	2026-08-19 16:47:23.877649
1417	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:47:23.877649
1418	simulation	HEALTHY	\N	2026-08-19 16:47:23.87865
1419	application	HEALTHY	4.5	2026-08-19 16:47:23.87865
1453	database	HEALTHY	0	2026-08-19 16:49:24.035361
1454	redis	NOT_CONFIGURED	\N	2026-08-19 16:49:24.035361
1455	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:49:24.035361
1456	celery	NOT_CONFIGURED	\N	2026-08-19 16:49:24.035361
1457	email	HEALTHY	\N	2026-08-19 16:49:24.035361
1458	backup	UNAVAILABLE	\N	2026-08-19 16:49:24.036359
1459	sentry	NOT_CONFIGURED	\N	2026-08-19 16:49:24.036359
1460	openai	NOT_CONFIGURED	\N	2026-08-19 16:49:24.036359
1461	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:49:24.036359
1462	simulation	HEALTHY	\N	2026-08-19 16:49:24.036359
1463	application	HEALTHY	4.5	2026-08-19 16:49:24.036359
1508	database	HEALTHY	4.99	2026-08-19 16:51:54.281725
1509	redis	NOT_CONFIGURED	\N	2026-08-19 16:51:54.281725
1510	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:51:54.281725
1511	celery	NOT_CONFIGURED	\N	2026-08-19 16:51:54.282728
1512	email	HEALTHY	\N	2026-08-19 16:51:54.282728
1513	backup	UNAVAILABLE	\N	2026-08-19 16:51:54.282728
1514	sentry	NOT_CONFIGURED	\N	2026-08-19 16:51:54.282728
1515	openai	NOT_CONFIGURED	\N	2026-08-19 16:51:54.282728
1516	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:51:54.282728
1517	simulation	HEALTHY	\N	2026-08-19 16:51:54.282728
1518	application	HEALTHY	4.5	2026-08-19 16:51:54.282728
1574	database	HEALTHY	1.08	2026-08-19 16:54:54.524623
1575	redis	NOT_CONFIGURED	\N	2026-08-19 16:54:54.524623
1576	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:54:54.524623
1577	celery	NOT_CONFIGURED	\N	2026-08-19 16:54:54.524623
562	database	HEALTHY	0	2026-08-19 16:08:49.807318
563	redis	NOT_CONFIGURED	\N	2026-08-19 16:08:49.807318
564	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:08:49.807318
565	celery	NOT_CONFIGURED	\N	2026-08-19 16:08:49.807318
566	email	HEALTHY	\N	2026-08-19 16:08:49.807318
567	backup	DEGRADED	\N	2026-08-19 16:08:49.807318
568	sentry	NOT_CONFIGURED	\N	2026-08-19 16:08:49.807318
569	openai	NOT_CONFIGURED	\N	2026-08-19 16:08:49.807318
570	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:08:49.807318
571	simulation	HEALTHY	\N	2026-08-19 16:08:49.807318
572	application	HEALTHY	4.5	2026-08-19 16:08:49.807318
573	database	HEALTHY	0.97	2026-08-19 16:09:19.84777
574	redis	NOT_CONFIGURED	\N	2026-08-19 16:09:19.84777
575	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:09:19.84777
576	celery	NOT_CONFIGURED	\N	2026-08-19 16:09:19.84777
577	email	HEALTHY	\N	2026-08-19 16:09:19.84777
578	backup	DEGRADED	\N	2026-08-19 16:09:19.84777
579	sentry	NOT_CONFIGURED	\N	2026-08-19 16:09:19.84777
580	openai	NOT_CONFIGURED	\N	2026-08-19 16:09:19.84777
581	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:09:19.84777
582	simulation	HEALTHY	\N	2026-08-19 16:09:19.84777
583	application	HEALTHY	4.5	2026-08-19 16:09:19.84777
584	database	HEALTHY	1	2026-08-19 16:09:49.883057
585	redis	NOT_CONFIGURED	\N	2026-08-19 16:09:49.883057
586	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:09:49.883057
587	celery	NOT_CONFIGURED	\N	2026-08-19 16:09:49.883057
588	email	HEALTHY	\N	2026-08-19 16:09:49.883057
589	backup	DEGRADED	\N	2026-08-19 16:09:49.883057
590	sentry	NOT_CONFIGURED	\N	2026-08-19 16:09:49.883057
591	openai	NOT_CONFIGURED	\N	2026-08-19 16:09:49.883057
592	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:09:49.883057
593	simulation	HEALTHY	\N	2026-08-19 16:09:49.883057
594	application	HEALTHY	4.5	2026-08-19 16:09:49.883057
595	database	HEALTHY	1	2026-08-19 16:10:19.927704
596	redis	NOT_CONFIGURED	\N	2026-08-19 16:10:19.927704
597	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:10:19.927704
598	celery	NOT_CONFIGURED	\N	2026-08-19 16:10:19.927704
599	email	HEALTHY	\N	2026-08-19 16:10:19.927704
600	backup	DEGRADED	\N	2026-08-19 16:10:19.927704
601	sentry	NOT_CONFIGURED	\N	2026-08-19 16:10:19.927704
602	openai	NOT_CONFIGURED	\N	2026-08-19 16:10:19.927704
603	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:10:19.927704
604	simulation	HEALTHY	\N	2026-08-19 16:10:19.927704
605	application	HEALTHY	4.5	2026-08-19 16:10:19.927704
606	database	HEALTHY	0	2026-08-19 16:10:49.9668
607	redis	NOT_CONFIGURED	\N	2026-08-19 16:10:49.9668
608	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:10:49.9668
609	celery	NOT_CONFIGURED	\N	2026-08-19 16:10:49.9668
610	email	HEALTHY	\N	2026-08-19 16:10:49.9668
611	backup	DEGRADED	\N	2026-08-19 16:10:49.9668
612	sentry	NOT_CONFIGURED	\N	2026-08-19 16:10:49.9668
613	openai	NOT_CONFIGURED	\N	2026-08-19 16:10:49.9668
614	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:10:49.9668
615	simulation	HEALTHY	\N	2026-08-19 16:10:49.9668
616	application	HEALTHY	4.5	2026-08-19 16:10:49.9668
617	database	HEALTHY	0	2026-08-19 16:11:20.002192
618	redis	NOT_CONFIGURED	\N	2026-08-19 16:11:20.002192
619	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:11:20.002192
620	celery	NOT_CONFIGURED	\N	2026-08-19 16:11:20.002192
621	email	HEALTHY	\N	2026-08-19 16:11:20.002192
622	backup	DEGRADED	\N	2026-08-19 16:11:20.002192
623	sentry	NOT_CONFIGURED	\N	2026-08-19 16:11:20.002192
624	openai	NOT_CONFIGURED	\N	2026-08-19 16:11:20.002192
625	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:11:20.002192
626	simulation	HEALTHY	\N	2026-08-19 16:11:20.002192
627	application	HEALTHY	4.5	2026-08-19 16:11:20.002192
628	database	HEALTHY	0	2026-08-19 16:11:50.04983
629	redis	NOT_CONFIGURED	\N	2026-08-19 16:11:50.04983
630	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:11:50.04983
631	celery	NOT_CONFIGURED	\N	2026-08-19 16:11:50.050895
632	email	HEALTHY	\N	2026-08-19 16:11:50.050895
633	backup	DEGRADED	\N	2026-08-19 16:11:50.050895
634	sentry	NOT_CONFIGURED	\N	2026-08-19 16:11:50.050895
635	openai	NOT_CONFIGURED	\N	2026-08-19 16:11:50.050895
636	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:11:50.050895
637	simulation	HEALTHY	\N	2026-08-19 16:11:50.050895
638	application	HEALTHY	4.5	2026-08-19 16:11:50.050895
639	database	HEALTHY	1	2026-08-19 16:12:20.079732
640	redis	NOT_CONFIGURED	\N	2026-08-19 16:12:20.079732
641	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:12:20.079732
642	celery	NOT_CONFIGURED	\N	2026-08-19 16:12:20.079732
643	email	HEALTHY	\N	2026-08-19 16:12:20.079732
644	backup	DEGRADED	\N	2026-08-19 16:12:20.079732
645	sentry	NOT_CONFIGURED	\N	2026-08-19 16:12:20.079732
646	openai	NOT_CONFIGURED	\N	2026-08-19 16:12:20.079732
647	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:12:20.079732
648	simulation	HEALTHY	\N	2026-08-19 16:12:20.079732
649	application	HEALTHY	4.5	2026-08-19 16:12:20.079732
650	database	HEALTHY	0	2026-08-19 16:12:50.133789
651	redis	NOT_CONFIGURED	\N	2026-08-19 16:12:50.133789
652	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:12:50.135114
653	celery	NOT_CONFIGURED	\N	2026-08-19 16:12:50.135114
654	email	HEALTHY	\N	2026-08-19 16:12:50.135114
655	backup	DEGRADED	\N	2026-08-19 16:12:50.135114
656	sentry	NOT_CONFIGURED	\N	2026-08-19 16:12:50.135114
657	openai	NOT_CONFIGURED	\N	2026-08-19 16:12:50.135114
658	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:12:50.135114
659	simulation	HEALTHY	\N	2026-08-19 16:12:50.135114
660	application	HEALTHY	4.5	2026-08-19 16:12:50.135114
661	database	HEALTHY	3	2026-08-19 16:13:20.207174
662	redis	NOT_CONFIGURED	\N	2026-08-19 16:13:20.207174
663	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:13:20.207174
664	celery	NOT_CONFIGURED	\N	2026-08-19 16:13:20.207174
665	email	HEALTHY	\N	2026-08-19 16:13:20.207174
666	backup	DEGRADED	\N	2026-08-19 16:13:20.207174
667	sentry	NOT_CONFIGURED	\N	2026-08-19 16:13:20.207174
668	openai	NOT_CONFIGURED	\N	2026-08-19 16:13:20.207174
669	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:13:20.207174
670	simulation	HEALTHY	\N	2026-08-19 16:13:20.208717
671	application	HEALTHY	4.5	2026-08-19 16:13:20.208717
672	database	HEALTHY	3.99	2026-08-19 16:13:50.405009
673	redis	NOT_CONFIGURED	\N	2026-08-19 16:13:50.40601
674	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:13:50.40601
675	celery	NOT_CONFIGURED	\N	2026-08-19 16:13:50.40601
676	email	HEALTHY	\N	2026-08-19 16:13:50.40601
677	backup	DEGRADED	\N	2026-08-19 16:13:50.40601
678	sentry	NOT_CONFIGURED	\N	2026-08-19 16:13:50.40601
679	openai	NOT_CONFIGURED	\N	2026-08-19 16:13:50.40601
680	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:13:50.40601
681	simulation	HEALTHY	\N	2026-08-19 16:13:50.40601
682	application	HEALTHY	4.5	2026-08-19 16:13:50.40601
683	database	HEALTHY	0	2026-08-19 16:14:20.625927
684	redis	NOT_CONFIGURED	\N	2026-08-19 16:14:20.625927
685	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:14:20.625927
686	celery	NOT_CONFIGURED	\N	2026-08-19 16:14:20.625927
687	email	HEALTHY	\N	2026-08-19 16:14:20.626928
688	backup	DEGRADED	\N	2026-08-19 16:14:20.626928
689	sentry	NOT_CONFIGURED	\N	2026-08-19 16:14:20.626928
690	openai	NOT_CONFIGURED	\N	2026-08-19 16:14:20.626928
691	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:14:20.626928
692	simulation	HEALTHY	\N	2026-08-19 16:14:20.626928
693	application	HEALTHY	4.5	2026-08-19 16:14:20.626928
694	database	HEALTHY	0.99	2026-08-19 16:14:50.668735
695	redis	NOT_CONFIGURED	\N	2026-08-19 16:14:50.668735
696	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:14:50.668735
697	celery	NOT_CONFIGURED	\N	2026-08-19 16:14:50.668735
698	email	HEALTHY	\N	2026-08-19 16:14:50.668735
699	backup	DEGRADED	\N	2026-08-19 16:14:50.668735
700	sentry	NOT_CONFIGURED	\N	2026-08-19 16:14:50.668735
701	openai	NOT_CONFIGURED	\N	2026-08-19 16:14:50.669736
702	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:14:50.669736
703	simulation	HEALTHY	\N	2026-08-19 16:14:50.669736
704	application	HEALTHY	4.5	2026-08-19 16:14:50.669736
705	database	HEALTHY	1.01	2026-08-19 16:15:20.70198
706	redis	NOT_CONFIGURED	\N	2026-08-19 16:15:20.70198
707	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:15:20.70198
708	celery	NOT_CONFIGURED	\N	2026-08-19 16:15:20.70198
709	email	HEALTHY	\N	2026-08-19 16:15:20.70198
710	backup	DEGRADED	\N	2026-08-19 16:15:20.702983
711	sentry	NOT_CONFIGURED	\N	2026-08-19 16:15:20.702983
712	openai	NOT_CONFIGURED	\N	2026-08-19 16:15:20.702983
713	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:15:20.702983
714	simulation	HEALTHY	\N	2026-08-19 16:15:20.702983
715	application	HEALTHY	4.5	2026-08-19 16:15:20.702983
716	database	HEALTHY	1.02	2026-08-19 16:15:50.762278
717	redis	NOT_CONFIGURED	\N	2026-08-19 16:15:50.762278
718	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:15:50.762278
719	celery	NOT_CONFIGURED	\N	2026-08-19 16:15:50.762278
720	email	HEALTHY	\N	2026-08-19 16:15:50.762278
721	backup	DEGRADED	\N	2026-08-19 16:15:50.762278
722	sentry	NOT_CONFIGURED	\N	2026-08-19 16:15:50.762278
723	openai	NOT_CONFIGURED	\N	2026-08-19 16:15:50.762278
724	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:15:50.762278
725	simulation	HEALTHY	\N	2026-08-19 16:15:50.762278
726	application	HEALTHY	4.5	2026-08-19 16:15:50.762278
727	database	HEALTHY	0	2026-08-19 16:16:20.807288
728	redis	NOT_CONFIGURED	\N	2026-08-19 16:16:20.807288
729	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:16:20.807288
730	celery	NOT_CONFIGURED	\N	2026-08-19 16:16:20.807288
731	email	HEALTHY	\N	2026-08-19 16:16:20.808291
732	backup	DEGRADED	\N	2026-08-19 16:16:20.808291
733	sentry	NOT_CONFIGURED	\N	2026-08-19 16:16:20.808291
734	openai	NOT_CONFIGURED	\N	2026-08-19 16:16:20.808291
735	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:16:20.808291
736	simulation	HEALTHY	\N	2026-08-19 16:16:20.808291
737	application	HEALTHY	4.5	2026-08-19 16:16:20.808291
738	database	HEALTHY	1	2026-08-19 16:16:50.86567
739	redis	NOT_CONFIGURED	\N	2026-08-19 16:16:50.86567
740	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:16:50.86567
741	celery	NOT_CONFIGURED	\N	2026-08-19 16:16:50.86567
742	email	HEALTHY	\N	2026-08-19 16:16:50.86567
743	backup	DEGRADED	\N	2026-08-19 16:16:50.86567
744	sentry	NOT_CONFIGURED	\N	2026-08-19 16:16:50.86567
745	openai	NOT_CONFIGURED	\N	2026-08-19 16:16:50.86567
746	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:16:50.86567
747	simulation	HEALTHY	\N	2026-08-19 16:16:50.86567
748	application	HEALTHY	4.5	2026-08-19 16:16:50.86567
749	database	HEALTHY	0	2026-08-19 16:17:20.900338
750	redis	NOT_CONFIGURED	\N	2026-08-19 16:17:20.900338
751	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:17:20.901367
752	celery	NOT_CONFIGURED	\N	2026-08-19 16:17:20.901367
753	email	HEALTHY	\N	2026-08-19 16:17:20.901367
754	backup	DEGRADED	\N	2026-08-19 16:17:20.901367
755	sentry	NOT_CONFIGURED	\N	2026-08-19 16:17:20.901367
756	openai	NOT_CONFIGURED	\N	2026-08-19 16:17:20.901367
757	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:17:20.901367
758	simulation	HEALTHY	\N	2026-08-19 16:17:20.901367
759	application	HEALTHY	4.5	2026-08-19 16:17:20.901367
760	database	HEALTHY	0.99	2026-08-19 16:17:50.958135
761	redis	NOT_CONFIGURED	\N	2026-08-19 16:17:50.958135
762	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:17:50.958135
763	celery	NOT_CONFIGURED	\N	2026-08-19 16:17:50.958135
764	email	HEALTHY	\N	2026-08-19 16:17:50.958135
765	backup	DEGRADED	\N	2026-08-19 16:17:50.958135
766	sentry	NOT_CONFIGURED	\N	2026-08-19 16:17:50.958135
767	openai	NOT_CONFIGURED	\N	2026-08-19 16:17:50.959133
768	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:17:50.959133
769	simulation	HEALTHY	\N	2026-08-19 16:17:50.959133
770	application	HEALTHY	4.5	2026-08-19 16:17:50.959133
771	database	HEALTHY	0	2026-08-19 16:18:20.992804
772	redis	NOT_CONFIGURED	\N	2026-08-19 16:18:20.993803
773	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:18:20.993803
774	celery	NOT_CONFIGURED	\N	2026-08-19 16:18:20.993803
775	email	HEALTHY	\N	2026-08-19 16:18:20.993803
776	backup	DEGRADED	\N	2026-08-19 16:18:20.993803
777	sentry	NOT_CONFIGURED	\N	2026-08-19 16:18:20.993803
778	openai	NOT_CONFIGURED	\N	2026-08-19 16:18:20.993803
779	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:18:20.993803
780	simulation	HEALTHY	\N	2026-08-19 16:18:20.993803
781	application	HEALTHY	4.5	2026-08-19 16:18:20.993803
782	database	HEALTHY	0	2026-08-19 16:18:51.042369
783	redis	NOT_CONFIGURED	\N	2026-08-19 16:18:51.042369
784	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:18:51.043367
785	celery	NOT_CONFIGURED	\N	2026-08-19 16:18:51.043367
786	email	HEALTHY	\N	2026-08-19 16:18:51.043367
787	backup	DEGRADED	\N	2026-08-19 16:18:51.043367
788	sentry	NOT_CONFIGURED	\N	2026-08-19 16:18:51.043367
789	openai	NOT_CONFIGURED	\N	2026-08-19 16:18:51.043367
790	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:18:51.043367
791	simulation	HEALTHY	\N	2026-08-19 16:18:51.043367
792	application	HEALTHY	4.5	2026-08-19 16:18:51.043367
793	database	HEALTHY	0	2026-08-19 16:19:21.075709
794	redis	NOT_CONFIGURED	\N	2026-08-19 16:19:21.075709
795	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:19:21.075709
796	celery	NOT_CONFIGURED	\N	2026-08-19 16:19:21.075709
797	email	HEALTHY	\N	2026-08-19 16:19:21.075709
798	backup	DEGRADED	\N	2026-08-19 16:19:21.075709
799	sentry	NOT_CONFIGURED	\N	2026-08-19 16:19:21.075709
800	openai	NOT_CONFIGURED	\N	2026-08-19 16:19:21.075709
801	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:19:21.075709
802	simulation	HEALTHY	\N	2026-08-19 16:19:21.075709
803	application	HEALTHY	4.5	2026-08-19 16:19:21.075709
804	database	HEALTHY	0	2026-08-19 16:19:51.108704
805	redis	NOT_CONFIGURED	\N	2026-08-19 16:19:51.108704
806	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:19:51.108704
807	celery	NOT_CONFIGURED	\N	2026-08-19 16:19:51.108704
808	email	HEALTHY	\N	2026-08-19 16:19:51.108704
809	backup	DEGRADED	\N	2026-08-19 16:19:51.108704
810	sentry	NOT_CONFIGURED	\N	2026-08-19 16:19:51.108704
811	openai	NOT_CONFIGURED	\N	2026-08-19 16:19:51.108704
812	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:19:51.109691
813	simulation	HEALTHY	\N	2026-08-19 16:19:51.109691
814	application	HEALTHY	4.5	2026-08-19 16:19:51.109691
815	database	HEALTHY	1	2026-08-19 16:20:21.135138
816	redis	NOT_CONFIGURED	\N	2026-08-19 16:20:21.135138
817	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:20:21.136481
818	celery	NOT_CONFIGURED	\N	2026-08-19 16:20:21.136481
819	email	HEALTHY	\N	2026-08-19 16:20:21.136481
820	backup	DEGRADED	\N	2026-08-19 16:20:21.136481
821	sentry	NOT_CONFIGURED	\N	2026-08-19 16:20:21.136481
822	openai	NOT_CONFIGURED	\N	2026-08-19 16:20:21.136481
823	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:20:21.136481
824	simulation	HEALTHY	\N	2026-08-19 16:20:21.136481
825	application	HEALTHY	4.5	2026-08-19 16:20:21.136481
826	database	HEALTHY	0.99	2026-08-19 16:20:51.174426
827	redis	NOT_CONFIGURED	\N	2026-08-19 16:20:51.174426
828	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:20:51.174426
829	celery	NOT_CONFIGURED	\N	2026-08-19 16:20:51.174426
830	email	HEALTHY	\N	2026-08-19 16:20:51.174426
831	backup	DEGRADED	\N	2026-08-19 16:20:51.174426
832	sentry	NOT_CONFIGURED	\N	2026-08-19 16:20:51.174426
833	openai	NOT_CONFIGURED	\N	2026-08-19 16:20:51.175438
834	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:20:51.175438
835	simulation	HEALTHY	\N	2026-08-19 16:20:51.175438
836	application	HEALTHY	4.5	2026-08-19 16:20:51.175438
837	database	HEALTHY	1	2026-08-19 16:21:21.215392
838	redis	NOT_CONFIGURED	\N	2026-08-19 16:21:21.216392
839	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:21:21.216392
840	celery	NOT_CONFIGURED	\N	2026-08-19 16:21:21.216392
841	email	HEALTHY	\N	2026-08-19 16:21:21.216392
842	backup	DEGRADED	\N	2026-08-19 16:21:21.216392
843	sentry	NOT_CONFIGURED	\N	2026-08-19 16:21:21.216392
844	openai	NOT_CONFIGURED	\N	2026-08-19 16:21:21.216392
845	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:21:21.216392
846	simulation	HEALTHY	\N	2026-08-19 16:21:21.216392
847	application	HEALTHY	4.5	2026-08-19 16:21:21.216392
848	database	HEALTHY	0	2026-08-19 16:21:51.250566
849	redis	NOT_CONFIGURED	\N	2026-08-19 16:21:51.250566
850	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:21:51.250566
851	celery	NOT_CONFIGURED	\N	2026-08-19 16:21:51.250566
852	email	HEALTHY	\N	2026-08-19 16:21:51.250566
853	backup	DEGRADED	\N	2026-08-19 16:21:51.252337
854	sentry	NOT_CONFIGURED	\N	2026-08-19 16:21:51.252337
855	openai	NOT_CONFIGURED	\N	2026-08-19 16:21:51.252337
856	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:21:51.252337
857	simulation	HEALTHY	\N	2026-08-19 16:21:51.252337
858	application	HEALTHY	4.5	2026-08-19 16:21:51.252337
859	database	HEALTHY	0.99	2026-08-19 16:22:21.278654
860	redis	NOT_CONFIGURED	\N	2026-08-19 16:22:21.278654
861	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:22:21.278654
862	celery	NOT_CONFIGURED	\N	2026-08-19 16:22:21.279694
863	email	HEALTHY	\N	2026-08-19 16:22:21.279694
864	backup	DEGRADED	\N	2026-08-19 16:22:21.279694
865	sentry	NOT_CONFIGURED	\N	2026-08-19 16:22:21.279694
866	openai	NOT_CONFIGURED	\N	2026-08-19 16:22:21.279694
867	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:22:21.279694
868	simulation	HEALTHY	\N	2026-08-19 16:22:21.279694
869	application	HEALTHY	4.5	2026-08-19 16:22:21.279694
870	database	HEALTHY	1	2026-08-19 16:22:51.337485
871	redis	NOT_CONFIGURED	\N	2026-08-19 16:22:51.337485
872	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:22:51.337485
873	celery	NOT_CONFIGURED	\N	2026-08-19 16:22:51.337485
874	email	HEALTHY	\N	2026-08-19 16:22:51.337485
875	backup	DEGRADED	\N	2026-08-19 16:22:51.337485
876	sentry	NOT_CONFIGURED	\N	2026-08-19 16:22:51.337485
877	openai	NOT_CONFIGURED	\N	2026-08-19 16:22:51.337485
878	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:22:51.337485
879	simulation	HEALTHY	\N	2026-08-19 16:22:51.337485
880	application	HEALTHY	4.5	2026-08-19 16:22:51.337485
881	database	HEALTHY	0	2026-08-19 16:23:21.363007
882	redis	NOT_CONFIGURED	\N	2026-08-19 16:23:21.363007
883	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:23:21.363007
884	celery	NOT_CONFIGURED	\N	2026-08-19 16:23:21.363007
885	email	HEALTHY	\N	2026-08-19 16:23:21.363007
886	backup	DEGRADED	\N	2026-08-19 16:23:21.363007
887	sentry	NOT_CONFIGURED	\N	2026-08-19 16:23:21.363007
888	openai	NOT_CONFIGURED	\N	2026-08-19 16:23:21.363007
889	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:23:21.364007
890	simulation	HEALTHY	\N	2026-08-19 16:23:21.364007
891	application	HEALTHY	4.5	2026-08-19 16:23:21.364007
892	database	HEALTHY	1	2026-08-19 16:23:51.414808
893	redis	NOT_CONFIGURED	\N	2026-08-19 16:23:51.415804
894	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:23:51.415804
895	celery	NOT_CONFIGURED	\N	2026-08-19 16:23:51.415804
896	email	HEALTHY	\N	2026-08-19 16:23:51.415804
897	backup	HEALTHY	\N	2026-08-19 16:23:51.415804
898	sentry	NOT_CONFIGURED	\N	2026-08-19 16:23:51.415804
899	openai	NOT_CONFIGURED	\N	2026-08-19 16:23:51.415804
900	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:23:51.415804
901	simulation	HEALTHY	\N	2026-08-19 16:23:51.415804
902	application	HEALTHY	4.5	2026-08-19 16:23:51.415804
903	database	HEALTHY	1.48	2026-08-19 16:24:21.444658
904	redis	NOT_CONFIGURED	\N	2026-08-19 16:24:21.446061
905	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:24:21.446061
906	celery	NOT_CONFIGURED	\N	2026-08-19 16:24:21.446061
907	email	HEALTHY	\N	2026-08-19 16:24:21.446061
908	backup	UNAVAILABLE	\N	2026-08-19 16:24:21.446061
909	sentry	NOT_CONFIGURED	\N	2026-08-19 16:24:21.446061
910	openai	NOT_CONFIGURED	\N	2026-08-19 16:24:21.446061
911	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:24:21.446061
912	simulation	HEALTHY	\N	2026-08-19 16:24:21.446061
913	application	HEALTHY	4.5	2026-08-19 16:24:21.446061
914	database	HEALTHY	1	2026-08-19 16:24:51.476468
915	redis	NOT_CONFIGURED	\N	2026-08-19 16:24:51.476468
916	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:24:51.476468
917	celery	NOT_CONFIGURED	\N	2026-08-19 16:24:51.476468
918	email	HEALTHY	\N	2026-08-19 16:24:51.476468
919	backup	UNAVAILABLE	\N	2026-08-19 16:24:51.476468
920	sentry	NOT_CONFIGURED	\N	2026-08-19 16:24:51.476468
921	openai	NOT_CONFIGURED	\N	2026-08-19 16:24:51.476468
922	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:24:51.476468
923	simulation	HEALTHY	\N	2026-08-19 16:24:51.476468
924	application	HEALTHY	4.5	2026-08-19 16:24:51.476468
925	database	HEALTHY	0	2026-08-19 16:25:21.502303
926	redis	NOT_CONFIGURED	\N	2026-08-19 16:25:21.503337
927	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:25:21.503337
928	celery	NOT_CONFIGURED	\N	2026-08-19 16:25:21.503337
929	email	HEALTHY	\N	2026-08-19 16:25:21.503337
930	backup	UNAVAILABLE	\N	2026-08-19 16:25:21.503337
931	sentry	NOT_CONFIGURED	\N	2026-08-19 16:25:21.503337
932	openai	NOT_CONFIGURED	\N	2026-08-19 16:25:21.503337
933	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:25:21.503337
934	simulation	HEALTHY	\N	2026-08-19 16:25:21.503337
935	application	HEALTHY	4.5	2026-08-19 16:25:21.503337
1244	database	HEALTHY	5	2026-08-19 16:39:52.867529
1245	redis	NOT_CONFIGURED	\N	2026-08-19 16:39:52.868526
1246	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:39:52.868526
1247	celery	NOT_CONFIGURED	\N	2026-08-19 16:39:52.868526
1248	email	HEALTHY	\N	2026-08-19 16:39:52.868526
1249	backup	UNAVAILABLE	\N	2026-08-19 16:39:52.868526
1250	sentry	NOT_CONFIGURED	\N	2026-08-19 16:39:52.868526
1251	openai	NOT_CONFIGURED	\N	2026-08-19 16:39:52.868526
1252	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:39:52.868526
1253	simulation	HEALTHY	\N	2026-08-19 16:39:52.868526
1254	application	HEALTHY	4.5	2026-08-19 16:39:52.868526
1365	database	HEALTHY	0	2026-08-19 16:45:23.700611
1366	redis	NOT_CONFIGURED	\N	2026-08-19 16:45:23.701999
1367	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:45:23.701999
1368	celery	NOT_CONFIGURED	\N	2026-08-19 16:45:23.701999
1369	email	HEALTHY	\N	2026-08-19 16:45:23.701999
1370	backup	UNAVAILABLE	\N	2026-08-19 16:45:23.701999
1371	sentry	NOT_CONFIGURED	\N	2026-08-19 16:45:23.701999
1372	openai	NOT_CONFIGURED	\N	2026-08-19 16:45:23.701999
1373	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:45:23.701999
1374	simulation	HEALTHY	\N	2026-08-19 16:45:23.701999
1375	application	HEALTHY	4.5	2026-08-19 16:45:23.70251
1420	database	HEALTHY	1	2026-08-19 16:47:53.920847
1421	redis	NOT_CONFIGURED	\N	2026-08-19 16:47:53.921847
1422	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:47:53.921847
1423	celery	NOT_CONFIGURED	\N	2026-08-19 16:47:53.921847
1424	email	HEALTHY	\N	2026-08-19 16:47:53.921847
1425	backup	UNAVAILABLE	\N	2026-08-19 16:47:53.921847
1426	sentry	NOT_CONFIGURED	\N	2026-08-19 16:47:53.921847
1427	openai	NOT_CONFIGURED	\N	2026-08-19 16:47:53.921847
1428	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:47:53.921847
1429	simulation	HEALTHY	\N	2026-08-19 16:47:53.921847
1430	application	HEALTHY	4.5	2026-08-19 16:47:53.921847
1519	database	HEALTHY	1.02	2026-08-19 16:52:24.329514
1520	redis	NOT_CONFIGURED	\N	2026-08-19 16:52:24.329514
1521	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:52:24.329514
1522	celery	NOT_CONFIGURED	\N	2026-08-19 16:52:24.329514
1523	email	HEALTHY	\N	2026-08-19 16:52:24.329514
1524	backup	UNAVAILABLE	\N	2026-08-19 16:52:24.330509
1525	sentry	NOT_CONFIGURED	\N	2026-08-19 16:52:24.330509
1526	openai	NOT_CONFIGURED	\N	2026-08-19 16:52:24.330509
1527	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:52:24.330509
1528	simulation	HEALTHY	\N	2026-08-19 16:52:24.330509
1529	application	HEALTHY	4.5	2026-08-19 16:52:24.330509
1618	database	HEALTHY	1	2026-08-19 16:56:54.646138
1619	redis	NOT_CONFIGURED	\N	2026-08-19 16:56:54.646138
1620	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:56:54.646138
1621	celery	NOT_CONFIGURED	\N	2026-08-19 16:56:54.646138
1622	email	HEALTHY	\N	2026-08-19 16:56:54.646138
1623	backup	UNAVAILABLE	\N	2026-08-19 16:56:54.646138
1624	sentry	NOT_CONFIGURED	\N	2026-08-19 16:56:54.646138
1625	openai	NOT_CONFIGURED	\N	2026-08-19 16:56:54.646138
1626	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:56:54.646138
1627	simulation	HEALTHY	\N	2026-08-19 16:56:54.646138
1628	application	HEALTHY	4.5	2026-08-19 16:56:54.646138
1640	database	HEALTHY	1	2026-08-19 16:57:54.722534
1641	redis	NOT_CONFIGURED	\N	2026-08-19 16:57:54.722534
1642	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:57:54.722534
1643	celery	NOT_CONFIGURED	\N	2026-08-19 16:57:54.722534
1644	email	HEALTHY	\N	2026-08-19 16:57:54.722534
1645	backup	UNAVAILABLE	\N	2026-08-19 16:57:54.722534
1646	sentry	NOT_CONFIGURED	\N	2026-08-19 16:57:54.722534
1647	openai	NOT_CONFIGURED	\N	2026-08-19 16:57:54.722534
1648	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:57:54.722534
1649	simulation	HEALTHY	\N	2026-08-19 16:57:54.722534
1650	application	HEALTHY	4.5	2026-08-19 16:57:54.722534
1728	database	HEALTHY	0	2026-08-19 17:01:55.137988
1729	redis	NOT_CONFIGURED	\N	2026-08-19 17:01:55.137988
1730	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:01:55.137988
1731	celery	NOT_CONFIGURED	\N	2026-08-19 17:01:55.137988
1732	email	HEALTHY	\N	2026-08-19 17:01:55.137988
1733	backup	UNAVAILABLE	\N	2026-08-19 17:01:55.137988
1734	sentry	NOT_CONFIGURED	\N	2026-08-19 17:01:55.137988
1735	openai	NOT_CONFIGURED	\N	2026-08-19 17:01:55.137988
1736	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:01:55.137988
1737	simulation	HEALTHY	\N	2026-08-19 17:01:55.137988
1738	application	HEALTHY	4.5	2026-08-19 17:01:55.137988
1882	database	HEALTHY	0.98	2026-08-19 17:08:55.627902
1883	redis	NOT_CONFIGURED	\N	2026-08-19 17:08:55.627902
1884	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:08:55.627902
1885	celery	NOT_CONFIGURED	\N	2026-08-19 17:08:55.627902
1886	email	HEALTHY	\N	2026-08-19 17:08:55.627902
1887	backup	UNAVAILABLE	\N	2026-08-19 17:08:55.627902
1888	sentry	NOT_CONFIGURED	\N	2026-08-19 17:08:55.627902
1889	openai	NOT_CONFIGURED	\N	2026-08-19 17:08:55.627902
1890	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:08:55.627902
1891	simulation	HEALTHY	\N	2026-08-19 17:08:55.627902
1892	application	HEALTHY	4.5	2026-08-19 17:08:55.627902
1920	backup	UNAVAILABLE	\N	2026-08-19 17:10:25.715988
1921	sentry	NOT_CONFIGURED	\N	2026-08-19 17:10:25.715988
1922	openai	NOT_CONFIGURED	\N	2026-08-19 17:10:25.715988
1923	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:10:25.715988
1924	simulation	HEALTHY	\N	2026-08-19 17:10:25.715988
1925	application	HEALTHY	4.5	2026-08-19 17:10:25.715988
1937	database	HEALTHY	1	2026-08-19 17:11:25.815368
1938	redis	NOT_CONFIGURED	\N	2026-08-19 17:11:25.815368
1939	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:11:25.815368
1940	celery	NOT_CONFIGURED	\N	2026-08-19 17:11:25.815368
1941	email	HEALTHY	\N	2026-08-19 17:11:25.816366
1942	backup	UNAVAILABLE	\N	2026-08-19 17:11:25.816366
1943	sentry	NOT_CONFIGURED	\N	2026-08-19 17:11:25.816366
1944	openai	NOT_CONFIGURED	\N	2026-08-19 17:11:25.816366
1945	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:11:25.816366
1946	simulation	HEALTHY	\N	2026-08-19 17:11:25.816366
1947	application	HEALTHY	4.5	2026-08-19 17:11:25.816366
1959	database	HEALTHY	0	2026-08-19 17:12:25.894247
1960	redis	NOT_CONFIGURED	\N	2026-08-19 17:12:25.895254
1961	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:12:25.895254
1962	celery	NOT_CONFIGURED	\N	2026-08-19 17:12:25.895254
1963	email	HEALTHY	\N	2026-08-19 17:12:25.895254
1964	backup	UNAVAILABLE	\N	2026-08-19 17:12:25.895254
1965	sentry	NOT_CONFIGURED	\N	2026-08-19 17:12:25.895254
1966	openai	NOT_CONFIGURED	\N	2026-08-19 17:12:25.895254
1967	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:12:25.895254
1968	simulation	HEALTHY	\N	2026-08-19 17:12:25.895254
1969	application	HEALTHY	4.5	2026-08-19 17:12:25.895254
1979	simulation	HEALTHY	\N	2026-08-19 17:12:55.919062
1980	application	HEALTHY	4.5	2026-08-19 17:12:55.919062
1981	database	HEALTHY	1	2026-08-19 17:13:25.942114
1982	redis	NOT_CONFIGURED	\N	2026-08-19 17:13:25.942114
1983	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:13:25.942114
1984	celery	NOT_CONFIGURED	\N	2026-08-19 17:13:25.942114
936	database	HEALTHY	1.02	2026-08-19 16:25:51.532387
937	redis	NOT_CONFIGURED	\N	2026-08-19 16:25:51.532387
938	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:25:51.532387
939	celery	NOT_CONFIGURED	\N	2026-08-19 16:25:51.53339
940	email	HEALTHY	\N	2026-08-19 16:25:51.53339
941	backup	UNAVAILABLE	\N	2026-08-19 16:25:51.53339
942	sentry	NOT_CONFIGURED	\N	2026-08-19 16:25:51.53339
943	openai	NOT_CONFIGURED	\N	2026-08-19 16:25:51.53339
944	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:25:51.53339
945	simulation	HEALTHY	\N	2026-08-19 16:25:51.53339
946	application	HEALTHY	4.5	2026-08-19 16:25:51.53339
947	database	HEALTHY	1.2	2026-08-19 16:26:21.566467
948	redis	NOT_CONFIGURED	\N	2026-08-19 16:26:21.566467
949	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:26:21.566467
950	celery	NOT_CONFIGURED	\N	2026-08-19 16:26:21.566467
951	email	HEALTHY	\N	2026-08-19 16:26:21.566467
952	backup	UNAVAILABLE	\N	2026-08-19 16:26:21.566467
953	sentry	NOT_CONFIGURED	\N	2026-08-19 16:26:21.567666
954	openai	NOT_CONFIGURED	\N	2026-08-19 16:26:21.567666
955	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:26:21.567666
956	simulation	HEALTHY	\N	2026-08-19 16:26:21.567666
957	application	HEALTHY	4.5	2026-08-19 16:26:21.567666
958	database	HEALTHY	0	2026-08-19 16:26:51.709669
959	redis	NOT_CONFIGURED	\N	2026-08-19 16:26:51.709669
960	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:26:51.709669
961	celery	NOT_CONFIGURED	\N	2026-08-19 16:26:51.709669
962	email	HEALTHY	\N	2026-08-19 16:26:51.709669
963	backup	UNAVAILABLE	\N	2026-08-19 16:26:51.709669
964	sentry	NOT_CONFIGURED	\N	2026-08-19 16:26:51.709669
965	openai	NOT_CONFIGURED	\N	2026-08-19 16:26:51.709669
966	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:26:51.709669
967	simulation	HEALTHY	\N	2026-08-19 16:26:51.709669
968	application	HEALTHY	4.5	2026-08-19 16:26:51.709669
969	database	HEALTHY	0	2026-08-19 16:27:21.740383
970	redis	NOT_CONFIGURED	\N	2026-08-19 16:27:21.740383
971	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:27:21.740383
972	celery	NOT_CONFIGURED	\N	2026-08-19 16:27:21.740383
973	email	HEALTHY	\N	2026-08-19 16:27:21.740383
974	backup	UNAVAILABLE	\N	2026-08-19 16:27:21.740383
975	sentry	NOT_CONFIGURED	\N	2026-08-19 16:27:21.740383
976	openai	NOT_CONFIGURED	\N	2026-08-19 16:27:21.740383
977	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:27:21.740383
978	simulation	HEALTHY	\N	2026-08-19 16:27:21.740383
979	application	HEALTHY	4.5	2026-08-19 16:27:21.740383
980	database	HEALTHY	2.99	2026-08-19 16:27:51.799375
981	redis	NOT_CONFIGURED	\N	2026-08-19 16:27:51.799375
982	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:27:51.799375
983	celery	NOT_CONFIGURED	\N	2026-08-19 16:27:51.799375
984	email	HEALTHY	\N	2026-08-19 16:27:51.799375
985	backup	UNAVAILABLE	\N	2026-08-19 16:27:51.799375
986	sentry	NOT_CONFIGURED	\N	2026-08-19 16:27:51.799375
987	openai	NOT_CONFIGURED	\N	2026-08-19 16:27:51.799375
988	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:27:51.799375
989	simulation	HEALTHY	\N	2026-08-19 16:27:51.799375
990	application	HEALTHY	4.5	2026-08-19 16:27:51.799375
991	database	HEALTHY	1	2026-08-19 16:28:21.849607
992	redis	NOT_CONFIGURED	\N	2026-08-19 16:28:21.849607
993	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:28:21.849607
994	celery	NOT_CONFIGURED	\N	2026-08-19 16:28:21.849607
995	email	HEALTHY	\N	2026-08-19 16:28:21.849607
996	backup	UNAVAILABLE	\N	2026-08-19 16:28:21.849607
997	sentry	NOT_CONFIGURED	\N	2026-08-19 16:28:21.849607
998	openai	NOT_CONFIGURED	\N	2026-08-19 16:28:21.849607
999	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:28:21.849607
1000	simulation	HEALTHY	\N	2026-08-19 16:28:21.849607
1001	application	HEALTHY	4.5	2026-08-19 16:28:21.849607
1002	database	HEALTHY	1.01	2026-08-19 16:28:51.88422
1003	redis	NOT_CONFIGURED	\N	2026-08-19 16:28:51.88422
1004	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:28:51.88422
1005	celery	NOT_CONFIGURED	\N	2026-08-19 16:28:51.88422
1006	email	HEALTHY	\N	2026-08-19 16:28:51.88422
1007	backup	UNAVAILABLE	\N	2026-08-19 16:28:51.88422
1008	sentry	NOT_CONFIGURED	\N	2026-08-19 16:28:51.88422
1009	openai	NOT_CONFIGURED	\N	2026-08-19 16:28:51.88422
1010	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:28:51.88422
1011	simulation	HEALTHY	\N	2026-08-19 16:28:51.88422
1012	application	HEALTHY	4.5	2026-08-19 16:28:51.88422
1013	database	HEALTHY	0	2026-08-19 16:29:21.917869
1014	redis	NOT_CONFIGURED	\N	2026-08-19 16:29:21.917869
1015	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:29:21.917869
1016	celery	NOT_CONFIGURED	\N	2026-08-19 16:29:21.917869
1017	email	HEALTHY	\N	2026-08-19 16:29:21.917869
1018	backup	UNAVAILABLE	\N	2026-08-19 16:29:21.917869
1019	sentry	NOT_CONFIGURED	\N	2026-08-19 16:29:21.917869
1020	openai	NOT_CONFIGURED	\N	2026-08-19 16:29:21.918885
1021	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:29:21.918885
1022	simulation	HEALTHY	\N	2026-08-19 16:29:21.918885
1023	application	HEALTHY	4.5	2026-08-19 16:29:21.918885
1024	database	HEALTHY	0	2026-08-19 16:29:51.951829
1025	redis	NOT_CONFIGURED	\N	2026-08-19 16:29:51.951829
1026	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:29:51.951829
1027	celery	NOT_CONFIGURED	\N	2026-08-19 16:29:51.951829
1028	email	HEALTHY	\N	2026-08-19 16:29:51.951829
1029	backup	UNAVAILABLE	\N	2026-08-19 16:29:51.951829
1030	sentry	NOT_CONFIGURED	\N	2026-08-19 16:29:51.951829
1031	openai	NOT_CONFIGURED	\N	2026-08-19 16:29:51.951829
1032	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:29:51.951829
1033	simulation	HEALTHY	\N	2026-08-19 16:29:51.951829
1034	application	HEALTHY	4.5	2026-08-19 16:29:51.951829
1035	database	HEALTHY	0	2026-08-19 16:30:21.983472
1036	redis	NOT_CONFIGURED	\N	2026-08-19 16:30:21.983472
1037	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:30:21.983472
1038	celery	NOT_CONFIGURED	\N	2026-08-19 16:30:21.983472
1039	email	HEALTHY	\N	2026-08-19 16:30:21.983472
1040	backup	UNAVAILABLE	\N	2026-08-19 16:30:21.983472
1041	sentry	NOT_CONFIGURED	\N	2026-08-19 16:30:21.983472
1042	openai	NOT_CONFIGURED	\N	2026-08-19 16:30:21.98526
1043	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:30:21.98526
1044	simulation	HEALTHY	\N	2026-08-19 16:30:21.98526
1045	application	HEALTHY	4.5	2026-08-19 16:30:21.98526
1046	database	HEALTHY	0	2026-08-19 16:30:52.00886
1047	redis	NOT_CONFIGURED	\N	2026-08-19 16:30:52.00886
1048	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:30:52.00886
1049	celery	NOT_CONFIGURED	\N	2026-08-19 16:30:52.00886
1050	email	HEALTHY	\N	2026-08-19 16:30:52.00886
1051	backup	UNAVAILABLE	\N	2026-08-19 16:30:52.00886
1052	sentry	NOT_CONFIGURED	\N	2026-08-19 16:30:52.00886
1053	openai	NOT_CONFIGURED	\N	2026-08-19 16:30:52.00886
1054	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:30:52.00886
1055	simulation	HEALTHY	\N	2026-08-19 16:30:52.00886
1056	application	HEALTHY	4.5	2026-08-19 16:30:52.00886
1057	database	HEALTHY	4	2026-08-19 16:31:22.11501
1058	redis	NOT_CONFIGURED	\N	2026-08-19 16:31:22.11501
1059	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:31:22.116014
1060	celery	NOT_CONFIGURED	\N	2026-08-19 16:31:22.116014
1061	email	HEALTHY	\N	2026-08-19 16:31:22.116014
1062	backup	UNAVAILABLE	\N	2026-08-19 16:31:22.116014
1063	sentry	NOT_CONFIGURED	\N	2026-08-19 16:31:22.116014
1064	openai	NOT_CONFIGURED	\N	2026-08-19 16:31:22.116014
1065	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:31:22.116014
1066	simulation	HEALTHY	\N	2026-08-19 16:31:22.116014
1067	application	HEALTHY	4.5	2026-08-19 16:31:22.116014
1255	database	HEALTHY	1	2026-08-19 16:40:22.915684
1256	redis	NOT_CONFIGURED	\N	2026-08-19 16:40:22.916712
1257	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:40:22.916712
1258	celery	NOT_CONFIGURED	\N	2026-08-19 16:40:22.916712
1259	email	HEALTHY	\N	2026-08-19 16:40:22.916712
1260	backup	UNAVAILABLE	\N	2026-08-19 16:40:22.916712
1261	sentry	NOT_CONFIGURED	\N	2026-08-19 16:40:22.916712
1262	openai	NOT_CONFIGURED	\N	2026-08-19 16:40:22.916712
1263	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:40:22.916712
1264	simulation	HEALTHY	\N	2026-08-19 16:40:22.916712
1265	application	HEALTHY	4.5	2026-08-19 16:40:22.916712
1266	database	HEALTHY	1.02	2026-08-19 16:40:52.952825
1267	redis	NOT_CONFIGURED	\N	2026-08-19 16:40:52.952825
1268	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:40:52.952825
1269	celery	NOT_CONFIGURED	\N	2026-08-19 16:40:52.952825
1270	email	HEALTHY	\N	2026-08-19 16:40:52.952825
1271	backup	UNAVAILABLE	\N	2026-08-19 16:40:52.952825
1272	sentry	NOT_CONFIGURED	\N	2026-08-19 16:40:52.952825
1273	openai	NOT_CONFIGURED	\N	2026-08-19 16:40:52.952825
1274	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:40:52.952825
1275	simulation	HEALTHY	\N	2026-08-19 16:40:52.952825
1276	application	HEALTHY	4.5	2026-08-19 16:40:52.953826
1398	database	HEALTHY	1	2026-08-19 16:46:53.826913
1399	redis	NOT_CONFIGURED	\N	2026-08-19 16:46:53.826913
1400	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:46:53.826913
1401	celery	NOT_CONFIGURED	\N	2026-08-19 16:46:53.826913
1402	email	HEALTHY	\N	2026-08-19 16:46:53.826913
1403	backup	UNAVAILABLE	\N	2026-08-19 16:46:53.826913
1404	sentry	NOT_CONFIGURED	\N	2026-08-19 16:46:53.826913
1405	openai	NOT_CONFIGURED	\N	2026-08-19 16:46:53.826913
1406	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:46:53.826913
1407	simulation	HEALTHY	\N	2026-08-19 16:46:53.826913
1408	application	HEALTHY	4.5	2026-08-19 16:46:53.826913
1431	database	HEALTHY	0	2026-08-19 16:48:23.956056
1432	redis	NOT_CONFIGURED	\N	2026-08-19 16:48:23.956056
1433	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:48:23.956056
1434	celery	NOT_CONFIGURED	\N	2026-08-19 16:48:23.956056
1435	email	HEALTHY	\N	2026-08-19 16:48:23.956056
1436	backup	UNAVAILABLE	\N	2026-08-19 16:48:23.956056
1437	sentry	NOT_CONFIGURED	\N	2026-08-19 16:48:23.956056
1438	openai	NOT_CONFIGURED	\N	2026-08-19 16:48:23.956056
1439	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:48:23.956056
1440	simulation	HEALTHY	\N	2026-08-19 16:48:23.956056
1441	application	HEALTHY	4.5	2026-08-19 16:48:23.956056
1530	database	HEALTHY	1	2026-08-19 16:52:54.367201
1531	redis	NOT_CONFIGURED	\N	2026-08-19 16:52:54.367201
1532	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:52:54.368216
1533	celery	NOT_CONFIGURED	\N	2026-08-19 16:52:54.368216
1534	email	HEALTHY	\N	2026-08-19 16:52:54.368216
1535	backup	UNAVAILABLE	\N	2026-08-19 16:52:54.368216
1536	sentry	NOT_CONFIGURED	\N	2026-08-19 16:52:54.368216
1537	openai	NOT_CONFIGURED	\N	2026-08-19 16:52:54.368216
1538	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:52:54.368216
1539	simulation	HEALTHY	\N	2026-08-19 16:52:54.368216
1540	application	HEALTHY	4.5	2026-08-19 16:52:54.368216
1596	database	HEALTHY	1	2026-08-19 16:55:54.58314
1597	redis	NOT_CONFIGURED	\N	2026-08-19 16:55:54.584144
1598	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:55:54.584144
1599	celery	NOT_CONFIGURED	\N	2026-08-19 16:55:54.584144
1600	email	HEALTHY	\N	2026-08-19 16:55:54.585141
1601	backup	UNAVAILABLE	\N	2026-08-19 16:55:54.585141
1602	sentry	NOT_CONFIGURED	\N	2026-08-19 16:55:54.585141
1603	openai	NOT_CONFIGURED	\N	2026-08-19 16:55:54.585141
1604	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:55:54.585141
1605	simulation	HEALTHY	\N	2026-08-19 16:55:54.585141
1606	application	HEALTHY	4.5	2026-08-19 16:55:54.585141
1673	database	HEALTHY	0	2026-08-19 16:59:24.861661
1674	redis	NOT_CONFIGURED	\N	2026-08-19 16:59:24.861661
1675	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:59:24.861661
1676	celery	NOT_CONFIGURED	\N	2026-08-19 16:59:24.861661
1677	email	HEALTHY	\N	2026-08-19 16:59:24.861661
1678	backup	UNAVAILABLE	\N	2026-08-19 16:59:24.861661
1679	sentry	NOT_CONFIGURED	\N	2026-08-19 16:59:24.861661
1680	openai	NOT_CONFIGURED	\N	2026-08-19 16:59:24.862679
1681	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:59:24.862679
1682	simulation	HEALTHY	\N	2026-08-19 16:59:24.862679
1683	application	HEALTHY	4.5	2026-08-19 16:59:24.862679
1750	database	HEALTHY	0	2026-08-19 17:02:55.210583
1751	redis	NOT_CONFIGURED	\N	2026-08-19 17:02:55.210583
1752	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:02:55.210583
1753	celery	NOT_CONFIGURED	\N	2026-08-19 17:02:55.210583
1754	email	HEALTHY	\N	2026-08-19 17:02:55.210583
1755	backup	UNAVAILABLE	\N	2026-08-19 17:02:55.210583
1756	sentry	NOT_CONFIGURED	\N	2026-08-19 17:02:55.210583
1757	openai	NOT_CONFIGURED	\N	2026-08-19 17:02:55.210583
1758	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:02:55.210583
1759	simulation	HEALTHY	\N	2026-08-19 17:02:55.210583
1760	application	HEALTHY	4.5	2026-08-19 17:02:55.210583
1772	database	HEALTHY	1	2026-08-19 17:03:55.272424
1773	redis	NOT_CONFIGURED	\N	2026-08-19 17:03:55.272424
1774	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:03:55.273424
1775	celery	NOT_CONFIGURED	\N	2026-08-19 17:03:55.273424
1776	email	HEALTHY	\N	2026-08-19 17:03:55.273424
1777	backup	UNAVAILABLE	\N	2026-08-19 17:03:55.273424
1778	sentry	NOT_CONFIGURED	\N	2026-08-19 17:03:55.273424
1779	openai	NOT_CONFIGURED	\N	2026-08-19 17:03:55.273424
1780	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:03:55.273424
1781	simulation	HEALTHY	\N	2026-08-19 17:03:55.273424
1782	application	HEALTHY	4.5	2026-08-19 17:03:55.273424
1893	database	HEALTHY	0.99	2026-08-19 17:09:25.651834
1894	redis	NOT_CONFIGURED	\N	2026-08-19 17:09:25.651834
1895	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:09:25.651834
1896	celery	NOT_CONFIGURED	\N	2026-08-19 17:09:25.651834
1897	email	HEALTHY	\N	2026-08-19 17:09:25.652832
1898	backup	UNAVAILABLE	\N	2026-08-19 17:09:25.652832
1899	sentry	NOT_CONFIGURED	\N	2026-08-19 17:09:25.652832
1900	openai	NOT_CONFIGURED	\N	2026-08-19 17:09:25.652832
1901	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:09:25.652832
1902	simulation	HEALTHY	\N	2026-08-19 17:09:25.652832
1903	application	HEALTHY	4.5	2026-08-19 17:09:25.652832
1926	database	HEALTHY	0	2026-08-19 17:10:55.749965
1927	redis	NOT_CONFIGURED	\N	2026-08-19 17:10:55.749965
1928	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:10:55.749965
1929	celery	NOT_CONFIGURED	\N	2026-08-19 17:10:55.749965
1930	email	HEALTHY	\N	2026-08-19 17:10:55.749965
1931	backup	UNAVAILABLE	\N	2026-08-19 17:10:55.749965
1068	database	HEALTHY	0	2026-08-19 16:31:52.153956
1069	redis	NOT_CONFIGURED	\N	2026-08-19 16:31:52.154953
1070	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:31:52.154953
1071	celery	NOT_CONFIGURED	\N	2026-08-19 16:31:52.154953
1072	email	HEALTHY	\N	2026-08-19 16:31:52.154953
1073	backup	UNAVAILABLE	\N	2026-08-19 16:31:52.154953
1074	sentry	NOT_CONFIGURED	\N	2026-08-19 16:31:52.154953
1075	openai	NOT_CONFIGURED	\N	2026-08-19 16:31:52.154953
1076	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:31:52.154953
1077	simulation	HEALTHY	\N	2026-08-19 16:31:52.154953
1078	application	HEALTHY	4.5	2026-08-19 16:31:52.154953
1277	database	HEALTHY	0.99	2026-08-19 16:41:22.98843
1278	redis	NOT_CONFIGURED	\N	2026-08-19 16:41:22.98843
1279	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:41:22.98843
1280	celery	NOT_CONFIGURED	\N	2026-08-19 16:41:22.98843
1281	email	HEALTHY	\N	2026-08-19 16:41:22.98843
1282	backup	UNAVAILABLE	\N	2026-08-19 16:41:22.98843
1283	sentry	NOT_CONFIGURED	\N	2026-08-19 16:41:22.98843
1284	openai	NOT_CONFIGURED	\N	2026-08-19 16:41:22.98843
1285	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:41:22.98843
1286	simulation	HEALTHY	\N	2026-08-19 16:41:22.989435
1287	application	HEALTHY	4.5	2026-08-19 16:41:22.989435
1442	database	HEALTHY	0	2026-08-19 16:48:53.990295
1443	redis	NOT_CONFIGURED	\N	2026-08-19 16:48:53.990295
1444	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:48:53.990295
1445	celery	NOT_CONFIGURED	\N	2026-08-19 16:48:53.990295
1446	email	HEALTHY	\N	2026-08-19 16:48:53.990295
1447	backup	UNAVAILABLE	\N	2026-08-19 16:48:53.990295
1448	sentry	NOT_CONFIGURED	\N	2026-08-19 16:48:53.990295
1449	openai	NOT_CONFIGURED	\N	2026-08-19 16:48:53.990295
1450	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:48:53.990295
1451	simulation	HEALTHY	\N	2026-08-19 16:48:53.990295
1452	application	HEALTHY	4.5	2026-08-19 16:48:53.990295
1552	database	HEALTHY	1	2026-08-19 16:53:54.446557
1553	redis	NOT_CONFIGURED	\N	2026-08-19 16:53:54.446557
1554	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:53:54.446557
1555	celery	NOT_CONFIGURED	\N	2026-08-19 16:53:54.447557
1556	email	HEALTHY	\N	2026-08-19 16:53:54.447557
1557	backup	UNAVAILABLE	\N	2026-08-19 16:53:54.447557
1558	sentry	NOT_CONFIGURED	\N	2026-08-19 16:53:54.447557
1559	openai	NOT_CONFIGURED	\N	2026-08-19 16:53:54.447557
1560	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:53:54.447557
1561	simulation	HEALTHY	\N	2026-08-19 16:53:54.447557
1562	application	HEALTHY	4.5	2026-08-19 16:53:54.447557
1629	database	HEALTHY	1	2026-08-19 16:57:24.676924
1630	redis	NOT_CONFIGURED	\N	2026-08-19 16:57:24.676924
1631	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:57:24.676924
1632	celery	NOT_CONFIGURED	\N	2026-08-19 16:57:24.676924
1633	email	HEALTHY	\N	2026-08-19 16:57:24.676924
1634	backup	UNAVAILABLE	\N	2026-08-19 16:57:24.676924
1635	sentry	NOT_CONFIGURED	\N	2026-08-19 16:57:24.676924
1636	openai	NOT_CONFIGURED	\N	2026-08-19 16:57:24.676924
1637	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:57:24.676924
1638	simulation	HEALTHY	\N	2026-08-19 16:57:24.676924
1639	application	HEALTHY	4.5	2026-08-19 16:57:24.676924
1684	database	HEALTHY	0	2026-08-19 16:59:54.900707
1685	redis	NOT_CONFIGURED	\N	2026-08-19 16:59:54.900707
1686	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:59:54.900707
1687	celery	NOT_CONFIGURED	\N	2026-08-19 16:59:54.900707
1688	email	HEALTHY	\N	2026-08-19 16:59:54.900707
1689	backup	UNAVAILABLE	\N	2026-08-19 16:59:54.900707
1690	sentry	NOT_CONFIGURED	\N	2026-08-19 16:59:54.900707
1691	openai	NOT_CONFIGURED	\N	2026-08-19 16:59:54.900707
1692	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:59:54.900707
1693	simulation	HEALTHY	\N	2026-08-19 16:59:54.900707
1694	application	HEALTHY	4.5	2026-08-19 16:59:54.901707
1805	database	HEALTHY	0	2026-08-19 17:05:25.393812
1806	redis	NOT_CONFIGURED	\N	2026-08-19 17:05:25.393812
1807	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:05:25.395155
1808	celery	NOT_CONFIGURED	\N	2026-08-19 17:05:25.395155
1809	email	HEALTHY	\N	2026-08-19 17:05:25.395155
1810	backup	UNAVAILABLE	\N	2026-08-19 17:05:25.395155
1811	sentry	NOT_CONFIGURED	\N	2026-08-19 17:05:25.395155
1812	openai	NOT_CONFIGURED	\N	2026-08-19 17:05:25.395155
1813	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:05:25.395155
1814	simulation	HEALTHY	\N	2026-08-19 17:05:25.395155
1815	application	HEALTHY	4.5	2026-08-19 17:05:25.395155
1871	database	HEALTHY	1	2026-08-19 17:08:25.599105
1872	redis	NOT_CONFIGURED	\N	2026-08-19 17:08:25.599105
1873	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:08:25.599105
1874	celery	NOT_CONFIGURED	\N	2026-08-19 17:08:25.599105
1875	email	HEALTHY	\N	2026-08-19 17:08:25.600226
1876	backup	UNAVAILABLE	\N	2026-08-19 17:08:25.600226
1877	sentry	NOT_CONFIGURED	\N	2026-08-19 17:08:25.600226
1878	openai	NOT_CONFIGURED	\N	2026-08-19 17:08:25.600226
1879	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:08:25.600226
1880	simulation	HEALTHY	\N	2026-08-19 17:08:25.600226
1881	application	HEALTHY	4.5	2026-08-19 17:08:25.600226
1904	database	HEALTHY	0	2026-08-19 17:09:55.684407
1905	redis	NOT_CONFIGURED	\N	2026-08-19 17:09:55.684407
1906	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:09:55.684407
1907	celery	NOT_CONFIGURED	\N	2026-08-19 17:09:55.684407
1908	email	HEALTHY	\N	2026-08-19 17:09:55.684407
1909	backup	UNAVAILABLE	\N	2026-08-19 17:09:55.684407
1910	sentry	NOT_CONFIGURED	\N	2026-08-19 17:09:55.684407
1911	openai	NOT_CONFIGURED	\N	2026-08-19 17:09:55.684407
1912	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:09:55.685409
1913	simulation	HEALTHY	\N	2026-08-19 17:09:55.685409
1914	application	HEALTHY	4.5	2026-08-19 17:09:55.685409
1932	sentry	NOT_CONFIGURED	\N	2026-08-19 17:10:55.749965
1933	openai	NOT_CONFIGURED	\N	2026-08-19 17:10:55.749965
1934	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:10:55.749965
1935	simulation	HEALTHY	\N	2026-08-19 17:10:55.749965
1936	application	HEALTHY	4.5	2026-08-19 17:10:55.749965
1948	database	HEALTHY	0	2026-08-19 17:11:55.854241
1949	redis	NOT_CONFIGURED	\N	2026-08-19 17:11:55.854241
1950	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:11:55.854241
1951	celery	NOT_CONFIGURED	\N	2026-08-19 17:11:55.854241
1952	email	HEALTHY	\N	2026-08-19 17:11:55.854241
1953	backup	UNAVAILABLE	\N	2026-08-19 17:11:55.854241
1954	sentry	NOT_CONFIGURED	\N	2026-08-19 17:11:55.854241
1955	openai	NOT_CONFIGURED	\N	2026-08-19 17:11:55.854241
1956	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:11:55.854241
1957	simulation	HEALTHY	\N	2026-08-19 17:11:55.854241
1958	application	HEALTHY	4.5	2026-08-19 17:11:55.854241
1970	database	HEALTHY	1.03	2026-08-19 17:12:55.91806
1971	redis	NOT_CONFIGURED	\N	2026-08-19 17:12:55.91806
1972	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:12:55.91806
1973	celery	NOT_CONFIGURED	\N	2026-08-19 17:12:55.919062
1974	email	HEALTHY	\N	2026-08-19 17:12:55.919062
1975	backup	UNAVAILABLE	\N	2026-08-19 17:12:55.919062
1976	sentry	NOT_CONFIGURED	\N	2026-08-19 17:12:55.919062
1977	openai	NOT_CONFIGURED	\N	2026-08-19 17:12:55.919062
1978	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:12:55.919062
1079	database	HEALTHY	1.04	2026-08-19 16:32:22.185859
1080	redis	NOT_CONFIGURED	\N	2026-08-19 16:32:22.186818
1081	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:32:22.186818
1082	celery	NOT_CONFIGURED	\N	2026-08-19 16:32:22.186818
1083	email	HEALTHY	\N	2026-08-19 16:32:22.186818
1084	backup	UNAVAILABLE	\N	2026-08-19 16:32:22.186818
1085	sentry	NOT_CONFIGURED	\N	2026-08-19 16:32:22.186818
1086	openai	NOT_CONFIGURED	\N	2026-08-19 16:32:22.186818
1087	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:32:22.186818
1088	simulation	HEALTHY	\N	2026-08-19 16:32:22.186818
1089	application	HEALTHY	4.5	2026-08-19 16:32:22.186818
1288	database	HEALTHY	0	2026-08-19 16:41:53.039874
1289	redis	NOT_CONFIGURED	\N	2026-08-19 16:41:53.039874
1290	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:41:53.039874
1291	celery	NOT_CONFIGURED	\N	2026-08-19 16:41:53.039874
1292	email	HEALTHY	\N	2026-08-19 16:41:53.039874
1293	backup	UNAVAILABLE	\N	2026-08-19 16:41:53.039874
1294	sentry	NOT_CONFIGURED	\N	2026-08-19 16:41:53.039874
1295	openai	NOT_CONFIGURED	\N	2026-08-19 16:41:53.039874
1296	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:41:53.039874
1297	simulation	HEALTHY	\N	2026-08-19 16:41:53.039874
1298	application	HEALTHY	4.5	2026-08-19 16:41:53.039874
1310	database	HEALTHY	1	2026-08-19 16:42:53.12398
1311	redis	NOT_CONFIGURED	\N	2026-08-19 16:42:53.12398
1312	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:42:53.12398
1313	celery	NOT_CONFIGURED	\N	2026-08-19 16:42:53.125099
1314	email	HEALTHY	\N	2026-08-19 16:42:53.125099
1315	backup	UNAVAILABLE	\N	2026-08-19 16:42:53.125099
1316	sentry	NOT_CONFIGURED	\N	2026-08-19 16:42:53.125099
1317	openai	NOT_CONFIGURED	\N	2026-08-19 16:42:53.125099
1318	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:42:53.125099
1319	simulation	HEALTHY	\N	2026-08-19 16:42:53.125099
1320	application	HEALTHY	4.5	2026-08-19 16:42:53.125099
1332	database	HEALTHY	1.02	2026-08-19 16:43:53.236274
1333	redis	NOT_CONFIGURED	\N	2026-08-19 16:43:53.236274
1334	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:43:53.236274
1335	celery	NOT_CONFIGURED	\N	2026-08-19 16:43:53.236274
1336	email	HEALTHY	\N	2026-08-19 16:43:53.236274
1337	backup	UNAVAILABLE	\N	2026-08-19 16:43:53.236274
1338	sentry	NOT_CONFIGURED	\N	2026-08-19 16:43:53.236274
1339	openai	NOT_CONFIGURED	\N	2026-08-19 16:43:53.236274
1340	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:43:53.237251
1341	simulation	HEALTHY	\N	2026-08-19 16:43:53.237251
1342	application	HEALTHY	4.5	2026-08-19 16:43:53.237251
1475	database	HEALTHY	1.17	2026-08-19 16:50:24.100571
1476	redis	NOT_CONFIGURED	\N	2026-08-19 16:50:24.100571
1477	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:50:24.100571
1478	celery	NOT_CONFIGURED	\N	2026-08-19 16:50:24.100571
1479	email	HEALTHY	\N	2026-08-19 16:50:24.100571
1480	backup	UNAVAILABLE	\N	2026-08-19 16:50:24.100571
1481	sentry	NOT_CONFIGURED	\N	2026-08-19 16:50:24.100571
1482	openai	NOT_CONFIGURED	\N	2026-08-19 16:50:24.100571
1483	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:50:24.101579
1484	simulation	HEALTHY	\N	2026-08-19 16:50:24.101579
1485	application	HEALTHY	4.5	2026-08-19 16:50:24.101579
1541	database	HEALTHY	0.96	2026-08-19 16:53:24.409707
1542	redis	NOT_CONFIGURED	\N	2026-08-19 16:53:24.409707
1543	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:53:24.409707
1544	celery	NOT_CONFIGURED	\N	2026-08-19 16:53:24.409707
1545	email	HEALTHY	\N	2026-08-19 16:53:24.409707
1546	backup	UNAVAILABLE	\N	2026-08-19 16:53:24.409707
1547	sentry	NOT_CONFIGURED	\N	2026-08-19 16:53:24.409707
1548	openai	NOT_CONFIGURED	\N	2026-08-19 16:53:24.409707
1549	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:53:24.409707
1550	simulation	HEALTHY	\N	2026-08-19 16:53:24.409707
1551	application	HEALTHY	4.5	2026-08-19 16:53:24.409707
1563	database	HEALTHY	1	2026-08-19 16:54:24.482785
1564	redis	NOT_CONFIGURED	\N	2026-08-19 16:54:24.483784
1565	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:54:24.483784
1566	celery	NOT_CONFIGURED	\N	2026-08-19 16:54:24.483784
1567	email	HEALTHY	\N	2026-08-19 16:54:24.483784
1568	backup	UNAVAILABLE	\N	2026-08-19 16:54:24.483784
1569	sentry	NOT_CONFIGURED	\N	2026-08-19 16:54:24.483784
1570	openai	NOT_CONFIGURED	\N	2026-08-19 16:54:24.483784
1571	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:54:24.483784
1572	simulation	HEALTHY	\N	2026-08-19 16:54:24.483784
1573	application	HEALTHY	4.5	2026-08-19 16:54:24.483784
1651	database	HEALTHY	0	2026-08-19 16:58:24.777371
1652	redis	NOT_CONFIGURED	\N	2026-08-19 16:58:24.777371
1653	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:58:24.777371
1654	celery	NOT_CONFIGURED	\N	2026-08-19 16:58:24.777371
1655	email	HEALTHY	\N	2026-08-19 16:58:24.777371
1656	backup	UNAVAILABLE	\N	2026-08-19 16:58:24.778378
1657	sentry	NOT_CONFIGURED	\N	2026-08-19 16:58:24.778378
1658	openai	NOT_CONFIGURED	\N	2026-08-19 16:58:24.778378
1659	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:58:24.778378
1660	simulation	HEALTHY	\N	2026-08-19 16:58:24.778378
1661	application	HEALTHY	4.5	2026-08-19 16:58:24.778378
1695	database	HEALTHY	1	2026-08-19 17:00:24.962356
1696	redis	NOT_CONFIGURED	\N	2026-08-19 17:00:24.962356
1697	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:00:24.962356
1698	celery	NOT_CONFIGURED	\N	2026-08-19 17:00:24.962356
1699	email	HEALTHY	\N	2026-08-19 17:00:24.962356
1700	backup	UNAVAILABLE	\N	2026-08-19 17:00:24.962356
1701	sentry	NOT_CONFIGURED	\N	2026-08-19 17:00:24.963357
1702	openai	NOT_CONFIGURED	\N	2026-08-19 17:00:24.963357
1703	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:00:24.963357
1704	simulation	HEALTHY	\N	2026-08-19 17:00:24.963357
1705	application	HEALTHY	4.5	2026-08-19 17:00:24.963357
1739	database	HEALTHY	0	2026-08-19 17:02:25.177388
1740	redis	NOT_CONFIGURED	\N	2026-08-19 17:02:25.177388
1741	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:02:25.177388
1742	celery	NOT_CONFIGURED	\N	2026-08-19 17:02:25.177388
1743	email	HEALTHY	\N	2026-08-19 17:02:25.177388
1744	backup	UNAVAILABLE	\N	2026-08-19 17:02:25.177388
1745	sentry	NOT_CONFIGURED	\N	2026-08-19 17:02:25.177388
1746	openai	NOT_CONFIGURED	\N	2026-08-19 17:02:25.177388
1747	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:02:25.177388
1748	simulation	HEALTHY	\N	2026-08-19 17:02:25.177388
1749	application	HEALTHY	4.5	2026-08-19 17:02:25.177388
1816	database	HEALTHY	0.97	2026-08-19 17:05:55.431079
1817	redis	NOT_CONFIGURED	\N	2026-08-19 17:05:55.431079
1818	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:05:55.431079
1819	celery	NOT_CONFIGURED	\N	2026-08-19 17:05:55.431079
1820	email	HEALTHY	\N	2026-08-19 17:05:55.431079
1821	backup	UNAVAILABLE	\N	2026-08-19 17:05:55.431079
1822	sentry	NOT_CONFIGURED	\N	2026-08-19 17:05:55.431079
1823	openai	NOT_CONFIGURED	\N	2026-08-19 17:05:55.431079
1824	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:05:55.432081
1825	simulation	HEALTHY	\N	2026-08-19 17:05:55.432081
1826	application	HEALTHY	4.5	2026-08-19 17:05:55.432081
1827	database	HEALTHY	1	2026-08-19 17:06:25.467058
1828	redis	NOT_CONFIGURED	\N	2026-08-19 17:06:25.467058
1829	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:06:25.467058
1090	database	HEALTHY	0	2026-08-19 16:32:52.218544
1091	redis	NOT_CONFIGURED	\N	2026-08-19 16:32:52.218544
1092	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:32:52.218544
1093	celery	NOT_CONFIGURED	\N	2026-08-19 16:32:52.218544
1094	email	HEALTHY	\N	2026-08-19 16:32:52.218544
1095	backup	UNAVAILABLE	\N	2026-08-19 16:32:52.218544
1096	sentry	NOT_CONFIGURED	\N	2026-08-19 16:32:52.218544
1097	openai	NOT_CONFIGURED	\N	2026-08-19 16:32:52.218544
1098	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:32:52.218544
1099	simulation	HEALTHY	\N	2026-08-19 16:32:52.218544
1100	application	HEALTHY	4.5	2026-08-19 16:32:52.218544
1101	database	HEALTHY	0.99	2026-08-19 16:33:22.244293
1102	redis	NOT_CONFIGURED	\N	2026-08-19 16:33:22.245293
1103	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:33:22.245293
1104	celery	NOT_CONFIGURED	\N	2026-08-19 16:33:22.245293
1105	email	HEALTHY	\N	2026-08-19 16:33:22.245293
1106	backup	UNAVAILABLE	\N	2026-08-19 16:33:22.245293
1107	sentry	NOT_CONFIGURED	\N	2026-08-19 16:33:22.245293
1108	openai	NOT_CONFIGURED	\N	2026-08-19 16:33:22.245293
1109	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:33:22.245293
1110	simulation	HEALTHY	\N	2026-08-19 16:33:22.245293
1111	application	HEALTHY	4.5	2026-08-19 16:33:22.245293
1112	database	HEALTHY	3.11	2026-08-19 16:33:52.306064
1113	redis	NOT_CONFIGURED	\N	2026-08-19 16:33:52.306064
1114	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:33:52.306064
1115	celery	NOT_CONFIGURED	\N	2026-08-19 16:33:52.307043
1116	email	HEALTHY	\N	2026-08-19 16:33:52.307043
1117	backup	UNAVAILABLE	\N	2026-08-19 16:33:52.307043
1118	sentry	NOT_CONFIGURED	\N	2026-08-19 16:33:52.307043
1119	openai	NOT_CONFIGURED	\N	2026-08-19 16:33:52.307043
1120	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:33:52.307043
1121	simulation	HEALTHY	\N	2026-08-19 16:33:52.307043
1122	application	HEALTHY	4.5	2026-08-19 16:33:52.307043
1123	database	HEALTHY	0	2026-08-19 16:34:22.357495
1124	redis	NOT_CONFIGURED	\N	2026-08-19 16:34:22.357495
1125	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:34:22.357495
1126	celery	NOT_CONFIGURED	\N	2026-08-19 16:34:22.357495
1127	email	HEALTHY	\N	2026-08-19 16:34:22.357495
1128	backup	UNAVAILABLE	\N	2026-08-19 16:34:22.357495
1129	sentry	NOT_CONFIGURED	\N	2026-08-19 16:34:22.357495
1130	openai	NOT_CONFIGURED	\N	2026-08-19 16:34:22.357495
1131	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:34:22.357495
1132	simulation	HEALTHY	\N	2026-08-19 16:34:22.357495
1133	application	HEALTHY	4.5	2026-08-19 16:34:22.358492
1134	database	HEALTHY	1	2026-08-19 16:34:52.402575
1135	redis	NOT_CONFIGURED	\N	2026-08-19 16:34:52.403576
1136	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:34:52.403576
1137	celery	NOT_CONFIGURED	\N	2026-08-19 16:34:52.403576
1138	email	HEALTHY	\N	2026-08-19 16:34:52.403576
1139	backup	UNAVAILABLE	\N	2026-08-19 16:34:52.403576
1140	sentry	NOT_CONFIGURED	\N	2026-08-19 16:34:52.403576
1141	openai	NOT_CONFIGURED	\N	2026-08-19 16:34:52.403576
1142	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:34:52.403576
1143	simulation	HEALTHY	\N	2026-08-19 16:34:52.403576
1144	application	HEALTHY	4.5	2026-08-19 16:34:52.403576
1145	database	HEALTHY	0.97	2026-08-19 16:35:22.443843
1146	redis	NOT_CONFIGURED	\N	2026-08-19 16:35:22.443843
1147	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:35:22.443843
1148	celery	NOT_CONFIGURED	\N	2026-08-19 16:35:22.443843
1149	email	HEALTHY	\N	2026-08-19 16:35:22.443843
1150	backup	UNAVAILABLE	\N	2026-08-19 16:35:22.443843
1151	sentry	NOT_CONFIGURED	\N	2026-08-19 16:35:22.443843
1152	openai	NOT_CONFIGURED	\N	2026-08-19 16:35:22.443843
1153	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:35:22.443843
1154	simulation	HEALTHY	\N	2026-08-19 16:35:22.443843
1155	application	HEALTHY	4.5	2026-08-19 16:35:22.443843
1156	database	HEALTHY	0	2026-08-19 16:35:52.503398
1157	redis	NOT_CONFIGURED	\N	2026-08-19 16:35:52.503398
1158	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:35:52.503398
1159	celery	NOT_CONFIGURED	\N	2026-08-19 16:35:52.503398
1160	email	HEALTHY	\N	2026-08-19 16:35:52.503398
1161	backup	UNAVAILABLE	\N	2026-08-19 16:35:52.503398
1162	sentry	NOT_CONFIGURED	\N	2026-08-19 16:35:52.503398
1163	openai	NOT_CONFIGURED	\N	2026-08-19 16:35:52.503398
1164	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:35:52.503398
1165	simulation	HEALTHY	\N	2026-08-19 16:35:52.503398
1166	application	HEALTHY	4.5	2026-08-19 16:35:52.503398
1167	database	HEALTHY	1	2026-08-19 16:36:22.539664
1168	redis	NOT_CONFIGURED	\N	2026-08-19 16:36:22.539664
1169	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:36:22.539664
1170	celery	NOT_CONFIGURED	\N	2026-08-19 16:36:22.539664
1171	email	HEALTHY	\N	2026-08-19 16:36:22.539664
1172	backup	UNAVAILABLE	\N	2026-08-19 16:36:22.539664
1173	sentry	NOT_CONFIGURED	\N	2026-08-19 16:36:22.539664
1174	openai	NOT_CONFIGURED	\N	2026-08-19 16:36:22.539664
1175	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:36:22.539664
1176	simulation	HEALTHY	\N	2026-08-19 16:36:22.539664
1177	application	HEALTHY	4.5	2026-08-19 16:36:22.54062
1178	database	HEALTHY	0.97	2026-08-19 16:36:52.574143
1179	redis	NOT_CONFIGURED	\N	2026-08-19 16:36:52.574143
1180	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:36:52.574143
1181	celery	NOT_CONFIGURED	\N	2026-08-19 16:36:52.574143
1182	email	HEALTHY	\N	2026-08-19 16:36:52.574143
1183	backup	UNAVAILABLE	\N	2026-08-19 16:36:52.574143
1184	sentry	NOT_CONFIGURED	\N	2026-08-19 16:36:52.574143
1185	openai	NOT_CONFIGURED	\N	2026-08-19 16:36:52.574143
1186	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:36:52.574143
1187	simulation	HEALTHY	\N	2026-08-19 16:36:52.574143
1188	application	HEALTHY	4.5	2026-08-19 16:36:52.574143
1189	database	HEALTHY	0.99	2026-08-19 16:37:22.610649
1190	redis	NOT_CONFIGURED	\N	2026-08-19 16:37:22.610649
1191	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:37:22.610649
1192	celery	NOT_CONFIGURED	\N	2026-08-19 16:37:22.610649
1193	email	HEALTHY	\N	2026-08-19 16:37:22.610649
1194	backup	UNAVAILABLE	\N	2026-08-19 16:37:22.610649
1195	sentry	NOT_CONFIGURED	\N	2026-08-19 16:37:22.610649
1196	openai	NOT_CONFIGURED	\N	2026-08-19 16:37:22.610649
1197	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:37:22.610649
1198	simulation	HEALTHY	\N	2026-08-19 16:37:22.612
1199	application	HEALTHY	4.5	2026-08-19 16:37:22.612
1200	database	HEALTHY	0	2026-08-19 16:37:52.647498
1201	redis	NOT_CONFIGURED	\N	2026-08-19 16:37:52.647498
1202	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:37:52.647498
1203	celery	NOT_CONFIGURED	\N	2026-08-19 16:37:52.647498
1204	email	HEALTHY	\N	2026-08-19 16:37:52.647498
1205	backup	UNAVAILABLE	\N	2026-08-19 16:37:52.648498
1206	sentry	NOT_CONFIGURED	\N	2026-08-19 16:37:52.648498
1207	openai	NOT_CONFIGURED	\N	2026-08-19 16:37:52.648498
1208	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:37:52.648498
1209	simulation	HEALTHY	\N	2026-08-19 16:37:52.648498
1210	application	HEALTHY	4.5	2026-08-19 16:37:52.648498
1211	database	HEALTHY	1.01	2026-08-19 16:38:22.697947
1212	redis	NOT_CONFIGURED	\N	2026-08-19 16:38:22.698948
1213	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:38:22.698948
1214	celery	NOT_CONFIGURED	\N	2026-08-19 16:38:22.698948
1215	email	HEALTHY	\N	2026-08-19 16:38:22.698948
1216	backup	UNAVAILABLE	\N	2026-08-19 16:38:22.698948
1217	sentry	NOT_CONFIGURED	\N	2026-08-19 16:38:22.698948
1218	openai	NOT_CONFIGURED	\N	2026-08-19 16:38:22.698948
1219	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:38:22.698948
1220	simulation	HEALTHY	\N	2026-08-19 16:38:22.698948
1221	application	HEALTHY	4.5	2026-08-19 16:38:22.698948
1299	database	HEALTHY	1.01	2026-08-19 16:42:23.083042
1300	redis	NOT_CONFIGURED	\N	2026-08-19 16:42:23.083042
1301	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:42:23.083042
1302	celery	NOT_CONFIGURED	\N	2026-08-19 16:42:23.083042
1303	email	HEALTHY	\N	2026-08-19 16:42:23.083042
1304	backup	UNAVAILABLE	\N	2026-08-19 16:42:23.083042
1305	sentry	NOT_CONFIGURED	\N	2026-08-19 16:42:23.083042
1306	openai	NOT_CONFIGURED	\N	2026-08-19 16:42:23.083042
1307	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:42:23.083042
1308	simulation	HEALTHY	\N	2026-08-19 16:42:23.083042
1309	application	HEALTHY	4.5	2026-08-19 16:42:23.083042
1321	database	HEALTHY	3	2026-08-19 16:43:23.200799
1322	redis	NOT_CONFIGURED	\N	2026-08-19 16:43:23.200799
1323	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:43:23.200799
1324	celery	NOT_CONFIGURED	\N	2026-08-19 16:43:23.200799
1325	email	HEALTHY	\N	2026-08-19 16:43:23.200799
1326	backup	UNAVAILABLE	\N	2026-08-19 16:43:23.200799
1327	sentry	NOT_CONFIGURED	\N	2026-08-19 16:43:23.200799
1328	openai	NOT_CONFIGURED	\N	2026-08-19 16:43:23.200799
1329	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:43:23.200799
1330	simulation	HEALTHY	\N	2026-08-19 16:43:23.200799
1331	application	HEALTHY	4.5	2026-08-19 16:43:23.200799
1376	database	HEALTHY	0	2026-08-19 16:45:53.744071
1377	redis	NOT_CONFIGURED	\N	2026-08-19 16:45:53.744071
1378	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:45:53.744071
1379	celery	NOT_CONFIGURED	\N	2026-08-19 16:45:53.744071
1380	email	HEALTHY	\N	2026-08-19 16:45:53.744071
1381	backup	UNAVAILABLE	\N	2026-08-19 16:45:53.744071
1382	sentry	NOT_CONFIGURED	\N	2026-08-19 16:45:53.744071
1383	openai	NOT_CONFIGURED	\N	2026-08-19 16:45:53.744071
1384	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:45:53.744071
1385	simulation	HEALTHY	\N	2026-08-19 16:45:53.744071
1386	application	HEALTHY	4.5	2026-08-19 16:45:53.7451
1387	database	HEALTHY	1.09	2026-08-19 16:46:23.771516
1388	redis	NOT_CONFIGURED	\N	2026-08-19 16:46:23.771516
1389	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:46:23.771516
1390	celery	NOT_CONFIGURED	\N	2026-08-19 16:46:23.771516
1391	email	HEALTHY	\N	2026-08-19 16:46:23.771516
1392	backup	UNAVAILABLE	\N	2026-08-19 16:46:23.772522
1393	sentry	NOT_CONFIGURED	\N	2026-08-19 16:46:23.772522
1394	openai	NOT_CONFIGURED	\N	2026-08-19 16:46:23.772522
1395	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:46:23.772522
1396	simulation	HEALTHY	\N	2026-08-19 16:46:23.772522
1397	application	HEALTHY	4.5	2026-08-19 16:46:23.772522
1464	database	HEALTHY	0	2026-08-19 16:49:54.067979
1465	redis	NOT_CONFIGURED	\N	2026-08-19 16:49:54.067979
1466	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:49:54.067979
1467	celery	NOT_CONFIGURED	\N	2026-08-19 16:49:54.067979
1468	email	HEALTHY	\N	2026-08-19 16:49:54.067979
1469	backup	UNAVAILABLE	\N	2026-08-19 16:49:54.067979
1470	sentry	NOT_CONFIGURED	\N	2026-08-19 16:49:54.067979
1471	openai	NOT_CONFIGURED	\N	2026-08-19 16:49:54.067979
1472	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:49:54.067979
1473	simulation	HEALTHY	\N	2026-08-19 16:49:54.067979
1474	application	HEALTHY	4.5	2026-08-19 16:49:54.067979
1486	database	HEALTHY	0	2026-08-19 16:50:54.138581
1487	redis	NOT_CONFIGURED	\N	2026-08-19 16:50:54.139722
1488	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:50:54.139722
1489	celery	NOT_CONFIGURED	\N	2026-08-19 16:50:54.139722
1490	email	HEALTHY	\N	2026-08-19 16:50:54.139722
1491	backup	UNAVAILABLE	\N	2026-08-19 16:50:54.139722
1492	sentry	NOT_CONFIGURED	\N	2026-08-19 16:50:54.139722
1493	openai	NOT_CONFIGURED	\N	2026-08-19 16:50:54.139722
1494	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:50:54.139722
1495	simulation	HEALTHY	\N	2026-08-19 16:50:54.139722
1496	application	HEALTHY	4.5	2026-08-19 16:50:54.139722
1578	email	HEALTHY	\N	2026-08-19 16:54:54.524623
1579	backup	UNAVAILABLE	\N	2026-08-19 16:54:54.524623
1580	sentry	NOT_CONFIGURED	\N	2026-08-19 16:54:54.524623
1581	openai	NOT_CONFIGURED	\N	2026-08-19 16:54:54.524623
1582	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:54:54.524623
1583	simulation	HEALTHY	\N	2026-08-19 16:54:54.524623
1584	application	HEALTHY	4.5	2026-08-19 16:54:54.524623
1706	database	HEALTHY	1	2026-08-19 17:00:55.028197
1707	redis	NOT_CONFIGURED	\N	2026-08-19 17:00:55.028197
1708	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:00:55.028197
1709	celery	NOT_CONFIGURED	\N	2026-08-19 17:00:55.028197
1710	email	HEALTHY	\N	2026-08-19 17:00:55.028197
1711	backup	UNAVAILABLE	\N	2026-08-19 17:00:55.028197
1712	sentry	NOT_CONFIGURED	\N	2026-08-19 17:00:55.028197
1713	openai	NOT_CONFIGURED	\N	2026-08-19 17:00:55.029217
1714	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:00:55.029217
1715	simulation	HEALTHY	\N	2026-08-19 17:00:55.029217
1716	application	HEALTHY	4.5	2026-08-19 17:00:55.029217
1761	database	HEALTHY	0.61	2026-08-19 17:03:25.248021
1762	redis	NOT_CONFIGURED	\N	2026-08-19 17:03:25.248588
1763	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:03:25.248588
1764	celery	NOT_CONFIGURED	\N	2026-08-19 17:03:25.248588
1765	email	HEALTHY	\N	2026-08-19 17:03:25.248588
1766	backup	UNAVAILABLE	\N	2026-08-19 17:03:25.248588
1767	sentry	NOT_CONFIGURED	\N	2026-08-19 17:03:25.248588
1768	openai	NOT_CONFIGURED	\N	2026-08-19 17:03:25.248588
1769	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:03:25.248588
1770	simulation	HEALTHY	\N	2026-08-19 17:03:25.248588
1771	application	HEALTHY	4.5	2026-08-19 17:03:25.248588
1830	celery	NOT_CONFIGURED	\N	2026-08-19 17:06:25.467058
1831	email	HEALTHY	\N	2026-08-19 17:06:25.467058
1832	backup	UNAVAILABLE	\N	2026-08-19 17:06:25.467058
1833	sentry	NOT_CONFIGURED	\N	2026-08-19 17:06:25.467058
1834	openai	NOT_CONFIGURED	\N	2026-08-19 17:06:25.467058
1835	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:06:25.46803
1836	simulation	HEALTHY	\N	2026-08-19 17:06:25.46803
1837	application	HEALTHY	4.5	2026-08-19 17:06:25.46803
1838	database	HEALTHY	1	2026-08-19 17:06:55.509036
1839	redis	NOT_CONFIGURED	\N	2026-08-19 17:06:55.509036
1840	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:06:55.509036
1841	celery	NOT_CONFIGURED	\N	2026-08-19 17:06:55.509036
1842	email	HEALTHY	\N	2026-08-19 17:06:55.509036
1843	backup	UNAVAILABLE	\N	2026-08-19 17:06:55.509036
1844	sentry	NOT_CONFIGURED	\N	2026-08-19 17:06:55.509036
1845	openai	NOT_CONFIGURED	\N	2026-08-19 17:06:55.509036
1846	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:06:55.509036
1847	simulation	HEALTHY	\N	2026-08-19 17:06:55.509036
1848	application	HEALTHY	4.5	2026-08-19 17:06:55.509036
1915	database	HEALTHY	0	2026-08-19 17:10:25.715988
1916	redis	NOT_CONFIGURED	\N	2026-08-19 17:10:25.715988
1222	database	HEALTHY	1	2026-08-19 16:38:52.727668
1223	redis	NOT_CONFIGURED	\N	2026-08-19 16:38:52.728667
1224	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:38:52.728667
1225	celery	NOT_CONFIGURED	\N	2026-08-19 16:38:52.728667
1226	email	HEALTHY	\N	2026-08-19 16:38:52.728667
1227	backup	UNAVAILABLE	\N	2026-08-19 16:38:52.728667
1228	sentry	NOT_CONFIGURED	\N	2026-08-19 16:38:52.728667
1229	openai	NOT_CONFIGURED	\N	2026-08-19 16:38:52.728667
1230	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:38:52.728667
1231	simulation	HEALTHY	\N	2026-08-19 16:38:52.728667
1232	application	HEALTHY	4.5	2026-08-19 16:38:52.728667
1343	database	HEALTHY	4	2026-08-19 16:44:23.499576
1344	redis	NOT_CONFIGURED	\N	2026-08-19 16:44:23.499576
1345	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:44:23.499576
1346	celery	NOT_CONFIGURED	\N	2026-08-19 16:44:23.499576
1347	email	HEALTHY	\N	2026-08-19 16:44:23.499576
1348	backup	UNAVAILABLE	\N	2026-08-19 16:44:23.499576
1349	sentry	NOT_CONFIGURED	\N	2026-08-19 16:44:23.499576
1350	openai	NOT_CONFIGURED	\N	2026-08-19 16:44:23.499576
1351	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:44:23.499576
1352	simulation	HEALTHY	\N	2026-08-19 16:44:23.499576
1353	application	HEALTHY	4.5	2026-08-19 16:44:23.499576
1497	database	HEALTHY	0	2026-08-19 16:51:24.168832
1498	redis	NOT_CONFIGURED	\N	2026-08-19 16:51:24.168832
1499	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:51:24.168832
1500	celery	NOT_CONFIGURED	\N	2026-08-19 16:51:24.168832
1501	email	HEALTHY	\N	2026-08-19 16:51:24.168832
1502	backup	UNAVAILABLE	\N	2026-08-19 16:51:24.168832
1503	sentry	NOT_CONFIGURED	\N	2026-08-19 16:51:24.168832
1504	openai	NOT_CONFIGURED	\N	2026-08-19 16:51:24.168832
1505	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:51:24.168832
1506	simulation	HEALTHY	\N	2026-08-19 16:51:24.168832
1507	application	HEALTHY	4.5	2026-08-19 16:51:24.168832
1585	database	HEALTHY	0	2026-08-19 16:55:24.548226
1586	redis	NOT_CONFIGURED	\N	2026-08-19 16:55:24.548226
1587	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:55:24.548226
1588	celery	NOT_CONFIGURED	\N	2026-08-19 16:55:24.548226
1589	email	HEALTHY	\N	2026-08-19 16:55:24.548226
1590	backup	UNAVAILABLE	\N	2026-08-19 16:55:24.548226
1591	sentry	NOT_CONFIGURED	\N	2026-08-19 16:55:24.548226
1592	openai	NOT_CONFIGURED	\N	2026-08-19 16:55:24.548226
1593	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:55:24.548226
1594	simulation	HEALTHY	\N	2026-08-19 16:55:24.548226
1595	application	HEALTHY	4.5	2026-08-19 16:55:24.548226
1607	database	HEALTHY	1	2026-08-19 16:56:24.611586
1608	redis	NOT_CONFIGURED	\N	2026-08-19 16:56:24.611586
1609	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:56:24.611586
1610	celery	NOT_CONFIGURED	\N	2026-08-19 16:56:24.611586
1611	email	HEALTHY	\N	2026-08-19 16:56:24.612583
1612	backup	UNAVAILABLE	\N	2026-08-19 16:56:24.612583
1613	sentry	NOT_CONFIGURED	\N	2026-08-19 16:56:24.612583
1614	openai	NOT_CONFIGURED	\N	2026-08-19 16:56:24.612583
1615	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:56:24.612583
1616	simulation	HEALTHY	\N	2026-08-19 16:56:24.612583
1617	application	HEALTHY	4.5	2026-08-19 16:56:24.612583
1662	database	HEALTHY	0.99	2026-08-19 16:58:54.809106
1663	redis	NOT_CONFIGURED	\N	2026-08-19 16:58:54.809106
1664	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:58:54.809106
1665	celery	NOT_CONFIGURED	\N	2026-08-19 16:58:54.809106
1666	email	HEALTHY	\N	2026-08-19 16:58:54.809106
1667	backup	UNAVAILABLE	\N	2026-08-19 16:58:54.809106
1668	sentry	NOT_CONFIGURED	\N	2026-08-19 16:58:54.809106
1669	openai	NOT_CONFIGURED	\N	2026-08-19 16:58:54.809106
1670	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:58:54.809106
1671	simulation	HEALTHY	\N	2026-08-19 16:58:54.809106
1672	application	HEALTHY	4.5	2026-08-19 16:58:54.809106
1717	database	HEALTHY	0	2026-08-19 17:01:25.08102
1718	redis	NOT_CONFIGURED	\N	2026-08-19 17:01:25.08102
1719	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:01:25.08102
1720	celery	NOT_CONFIGURED	\N	2026-08-19 17:01:25.08102
1721	email	HEALTHY	\N	2026-08-19 17:01:25.082809
1722	backup	UNAVAILABLE	\N	2026-08-19 17:01:25.082809
1723	sentry	NOT_CONFIGURED	\N	2026-08-19 17:01:25.082809
1724	openai	NOT_CONFIGURED	\N	2026-08-19 17:01:25.082809
1725	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:01:25.082809
1726	simulation	HEALTHY	\N	2026-08-19 17:01:25.082809
1727	application	HEALTHY	4.5	2026-08-19 17:01:25.082809
1783	database	HEALTHY	0	2026-08-19 17:04:25.303586
1784	redis	NOT_CONFIGURED	\N	2026-08-19 17:04:25.303586
1785	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:04:25.303586
1786	celery	NOT_CONFIGURED	\N	2026-08-19 17:04:25.303586
1787	email	HEALTHY	\N	2026-08-19 17:04:25.304585
1788	backup	UNAVAILABLE	\N	2026-08-19 17:04:25.304585
1789	sentry	NOT_CONFIGURED	\N	2026-08-19 17:04:25.304585
1790	openai	NOT_CONFIGURED	\N	2026-08-19 17:04:25.304585
1791	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:04:25.304585
1792	simulation	HEALTHY	\N	2026-08-19 17:04:25.304585
1793	application	HEALTHY	4.5	2026-08-19 17:04:25.304585
1794	database	HEALTHY	2	2026-08-19 17:04:55.32883
1795	redis	NOT_CONFIGURED	\N	2026-08-19 17:04:55.32883
1796	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:04:55.32883
1797	celery	NOT_CONFIGURED	\N	2026-08-19 17:04:55.32883
1798	email	HEALTHY	\N	2026-08-19 17:04:55.32983
1799	backup	UNAVAILABLE	\N	2026-08-19 17:04:55.32983
1800	sentry	NOT_CONFIGURED	\N	2026-08-19 17:04:55.32983
1801	openai	NOT_CONFIGURED	\N	2026-08-19 17:04:55.32983
1802	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:04:55.32983
1803	simulation	HEALTHY	\N	2026-08-19 17:04:55.32983
1804	application	HEALTHY	4.5	2026-08-19 17:04:55.32983
1849	database	HEALTHY	0	2026-08-19 17:07:25.558209
1850	redis	NOT_CONFIGURED	\N	2026-08-19 17:07:25.558209
1851	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:07:25.558209
1852	celery	NOT_CONFIGURED	\N	2026-08-19 17:07:25.558209
1853	email	HEALTHY	\N	2026-08-19 17:07:25.558209
1854	backup	UNAVAILABLE	\N	2026-08-19 17:07:25.558209
1855	sentry	NOT_CONFIGURED	\N	2026-08-19 17:07:25.558209
1856	openai	NOT_CONFIGURED	\N	2026-08-19 17:07:25.558209
1857	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:07:25.558209
1858	simulation	HEALTHY	\N	2026-08-19 17:07:25.558209
1859	application	HEALTHY	4.5	2026-08-19 17:07:25.558209
1860	database	HEALTHY	0	2026-08-19 17:07:55.577508
1861	redis	NOT_CONFIGURED	\N	2026-08-19 17:07:55.577508
1862	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:07:55.577508
1863	celery	NOT_CONFIGURED	\N	2026-08-19 17:07:55.577508
1864	email	HEALTHY	\N	2026-08-19 17:07:55.577508
1865	backup	UNAVAILABLE	\N	2026-08-19 17:07:55.577508
1866	sentry	NOT_CONFIGURED	\N	2026-08-19 17:07:55.577508
1867	openai	NOT_CONFIGURED	\N	2026-08-19 17:07:55.577508
1868	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:07:55.577508
1869	simulation	HEALTHY	\N	2026-08-19 17:07:55.577508
1870	application	HEALTHY	4.5	2026-08-19 17:07:55.577508
1917	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:10:25.715988
1918	celery	NOT_CONFIGURED	\N	2026-08-19 17:10:25.715988
1919	email	HEALTHY	\N	2026-08-19 17:10:25.715988
1985	email	HEALTHY	\N	2026-08-19 17:13:25.943111
1986	backup	UNAVAILABLE	\N	2026-08-19 17:13:25.943111
1987	sentry	NOT_CONFIGURED	\N	2026-08-19 17:13:25.943111
1988	openai	NOT_CONFIGURED	\N	2026-08-19 17:13:25.943111
1989	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:13:25.943111
1990	simulation	HEALTHY	\N	2026-08-19 17:13:25.943111
1991	application	HEALTHY	4.5	2026-08-19 17:13:25.943111
2047	database	HEALTHY	0	2026-08-19 17:16:26.257628
2048	redis	NOT_CONFIGURED	\N	2026-08-19 17:16:26.257628
2049	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:16:26.257628
2050	celery	NOT_CONFIGURED	\N	2026-08-19 17:16:26.257628
2051	email	HEALTHY	\N	2026-08-19 17:16:26.257628
2052	backup	UNAVAILABLE	\N	2026-08-19 17:16:26.257628
2053	sentry	NOT_CONFIGURED	\N	2026-08-19 17:16:26.257628
2054	openai	NOT_CONFIGURED	\N	2026-08-19 17:16:26.257628
2055	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:16:26.257628
2056	simulation	HEALTHY	\N	2026-08-19 17:16:26.257628
2057	application	HEALTHY	4.5	2026-08-19 17:16:26.257628
2795	database	HEALTHY	0	2026-08-19 18:15:44.241289
2796	redis	NOT_CONFIGURED	\N	2026-08-19 18:15:44.241289
2797	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:15:44.241289
2798	celery	NOT_CONFIGURED	\N	2026-08-19 18:15:44.241289
2799	email	HEALTHY	\N	2026-08-19 18:15:44.241289
2800	backup	UNAVAILABLE	\N	2026-08-19 18:15:44.241289
2801	sentry	NOT_CONFIGURED	\N	2026-08-19 18:15:44.241289
2802	openai	NOT_CONFIGURED	\N	2026-08-19 18:15:44.242286
2803	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:15:44.242286
2804	simulation	HEALTHY	\N	2026-08-19 18:15:44.242286
2805	application	HEALTHY	4.5	2026-08-19 18:15:44.242286
2861	database	HEALTHY	0	2026-08-19 18:18:44.638647
2862	redis	NOT_CONFIGURED	\N	2026-08-19 18:18:44.638647
2863	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:18:44.638647
2864	celery	NOT_CONFIGURED	\N	2026-08-19 18:18:44.638647
2865	email	HEALTHY	\N	2026-08-19 18:18:44.638647
2866	backup	UNAVAILABLE	\N	2026-08-19 18:18:44.638647
2867	sentry	NOT_CONFIGURED	\N	2026-08-19 18:18:44.638647
2868	openai	NOT_CONFIGURED	\N	2026-08-19 18:18:44.638647
2869	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:18:44.638647
2870	simulation	HEALTHY	\N	2026-08-19 18:18:44.638647
2871	application	HEALTHY	4.5	2026-08-19 18:18:44.638647
3004	database	HEALTHY	1	2026-08-19 18:22:14.838535
3005	redis	NOT_CONFIGURED	\N	2026-08-19 18:22:14.838535
3006	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:22:14.838535
3007	celery	NOT_CONFIGURED	\N	2026-08-19 18:22:14.839526
3008	email	HEALTHY	\N	2026-08-19 18:22:14.839526
3009	backup	UNAVAILABLE	\N	2026-08-19 18:22:14.839526
3010	sentry	NOT_CONFIGURED	\N	2026-08-19 18:22:14.839526
3011	openai	NOT_CONFIGURED	\N	2026-08-19 18:22:14.839526
3012	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:22:14.839526
3013	simulation	HEALTHY	\N	2026-08-19 18:22:14.839526
3014	application	HEALTHY	4.5	2026-08-19 18:22:14.839526
3070	database	HEALTHY	0	2026-08-19 18:24:14.951309
3071	redis	NOT_CONFIGURED	\N	2026-08-19 18:24:14.951309
3072	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:24:14.951309
3073	celery	NOT_CONFIGURED	\N	2026-08-19 18:24:14.951309
3074	email	HEALTHY	\N	2026-08-19 18:24:14.951309
3075	backup	DEGRADED	\N	2026-08-19 18:24:14.951309
3076	sentry	NOT_CONFIGURED	\N	2026-08-19 18:24:14.951309
3077	openai	NOT_CONFIGURED	\N	2026-08-19 18:24:14.951309
3078	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:24:14.951309
3079	simulation	HEALTHY	\N	2026-08-19 18:24:14.951309
3080	application	HEALTHY	4.5	2026-08-19 18:24:14.951309
1992	database	HEALTHY	0.66	2026-08-19 17:13:55.979767
1993	redis	NOT_CONFIGURED	\N	2026-08-19 17:13:55.979767
1994	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:13:55.979767
1995	celery	NOT_CONFIGURED	\N	2026-08-19 17:13:55.980319
1996	email	HEALTHY	\N	2026-08-19 17:13:55.980319
1997	backup	UNAVAILABLE	\N	2026-08-19 17:13:55.980319
1998	sentry	NOT_CONFIGURED	\N	2026-08-19 17:13:55.980319
1999	openai	NOT_CONFIGURED	\N	2026-08-19 17:13:55.980319
2000	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:13:55.980319
2001	simulation	HEALTHY	\N	2026-08-19 17:13:55.980319
2002	application	HEALTHY	4.5	2026-08-19 17:13:55.980319
2003	database	HEALTHY	0	2026-08-19 17:14:26.015046
2004	redis	NOT_CONFIGURED	\N	2026-08-19 17:14:26.016049
2005	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:14:26.016049
2006	celery	NOT_CONFIGURED	\N	2026-08-19 17:14:26.016049
2007	email	HEALTHY	\N	2026-08-19 17:14:26.016049
2008	backup	UNAVAILABLE	\N	2026-08-19 17:14:26.016049
2009	sentry	NOT_CONFIGURED	\N	2026-08-19 17:14:26.016049
2010	openai	NOT_CONFIGURED	\N	2026-08-19 17:14:26.016049
2011	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:14:26.016049
2012	simulation	HEALTHY	\N	2026-08-19 17:14:26.016049
2013	application	HEALTHY	4.5	2026-08-19 17:14:26.016049
2058	database	HEALTHY	1	2026-08-19 17:16:56.278995
2059	redis	NOT_CONFIGURED	\N	2026-08-19 17:16:56.278995
2060	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:16:56.278995
2061	celery	NOT_CONFIGURED	\N	2026-08-19 17:16:56.278995
2062	email	HEALTHY	\N	2026-08-19 17:16:56.278995
2063	backup	UNAVAILABLE	\N	2026-08-19 17:16:56.278995
2064	sentry	NOT_CONFIGURED	\N	2026-08-19 17:16:56.278995
2065	openai	NOT_CONFIGURED	\N	2026-08-19 17:16:56.278995
2066	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:16:56.278995
2067	simulation	HEALTHY	\N	2026-08-19 17:16:56.278995
2068	application	HEALTHY	4.5	2026-08-19 17:16:56.278995
2069	database	HEALTHY	1	2026-08-19 17:17:26.301842
2070	redis	NOT_CONFIGURED	\N	2026-08-19 17:17:26.301842
2071	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:17:26.301842
2072	celery	NOT_CONFIGURED	\N	2026-08-19 17:17:26.301842
2073	email	HEALTHY	\N	2026-08-19 17:17:26.301842
2074	backup	UNAVAILABLE	\N	2026-08-19 17:17:26.301842
2075	sentry	NOT_CONFIGURED	\N	2026-08-19 17:17:26.301842
2076	openai	NOT_CONFIGURED	\N	2026-08-19 17:17:26.302842
2077	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:17:26.302842
2078	simulation	HEALTHY	\N	2026-08-19 17:17:26.302842
2079	application	HEALTHY	4.5	2026-08-19 17:17:26.302842
2091	database	HEALTHY	0	2026-08-19 17:18:26.381749
2092	redis	NOT_CONFIGURED	\N	2026-08-19 17:18:26.382749
2093	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:18:26.382749
2094	celery	NOT_CONFIGURED	\N	2026-08-19 17:18:26.382749
2095	email	HEALTHY	\N	2026-08-19 17:18:26.382749
2096	backup	UNAVAILABLE	\N	2026-08-19 17:18:26.382749
2097	sentry	NOT_CONFIGURED	\N	2026-08-19 17:18:26.382749
2098	openai	NOT_CONFIGURED	\N	2026-08-19 17:18:26.382749
2099	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:18:26.382749
2100	simulation	HEALTHY	\N	2026-08-19 17:18:26.382749
2101	application	HEALTHY	4.5	2026-08-19 17:18:26.382749
2806	database	HEALTHY	20	2026-08-19 18:16:14.352338
2807	redis	NOT_CONFIGURED	\N	2026-08-19 18:16:14.352338
2808	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:16:14.352338
2809	celery	NOT_CONFIGURED	\N	2026-08-19 18:16:14.352338
2810	email	HEALTHY	\N	2026-08-19 18:16:14.352338
2811	backup	UNAVAILABLE	\N	2026-08-19 18:16:14.352338
2812	sentry	NOT_CONFIGURED	\N	2026-08-19 18:16:14.352338
2813	openai	NOT_CONFIGURED	\N	2026-08-19 18:16:14.352338
2814	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:16:14.352338
2815	simulation	HEALTHY	\N	2026-08-19 18:16:14.352338
2816	application	HEALTHY	4.5	2026-08-19 18:16:14.352338
2817	database	HEALTHY	0	2026-08-19 18:16:44.445018
2818	redis	NOT_CONFIGURED	\N	2026-08-19 18:16:44.445018
2819	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:16:44.445018
2820	celery	NOT_CONFIGURED	\N	2026-08-19 18:16:44.445018
2821	email	HEALTHY	\N	2026-08-19 18:16:44.445018
2822	backup	UNAVAILABLE	\N	2026-08-19 18:16:44.445018
2823	sentry	NOT_CONFIGURED	\N	2026-08-19 18:16:44.446016
2824	openai	NOT_CONFIGURED	\N	2026-08-19 18:16:44.446016
2825	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:16:44.446016
2826	simulation	HEALTHY	\N	2026-08-19 18:16:44.446016
2827	application	HEALTHY	4.5	2026-08-19 18:16:44.446016
2839	database	HEALTHY	1	2026-08-19 18:17:44.557355
2840	redis	NOT_CONFIGURED	\N	2026-08-19 18:17:44.557355
2841	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:17:44.557355
2842	celery	NOT_CONFIGURED	\N	2026-08-19 18:17:44.557355
2843	email	HEALTHY	\N	2026-08-19 18:17:44.557355
2844	backup	UNAVAILABLE	\N	2026-08-19 18:17:44.557355
2845	sentry	NOT_CONFIGURED	\N	2026-08-19 18:17:44.557355
2846	openai	NOT_CONFIGURED	\N	2026-08-19 18:17:44.557355
2847	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:17:44.557355
2848	simulation	HEALTHY	\N	2026-08-19 18:17:44.557355
2849	application	HEALTHY	4.5	2026-08-19 18:17:44.557355
2938	database	HEALTHY	0	2026-08-19 18:20:44.759058
2939	redis	NOT_CONFIGURED	\N	2026-08-19 18:20:44.759058
2940	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:20:44.759058
2941	celery	NOT_CONFIGURED	\N	2026-08-19 18:20:44.759058
2942	email	HEALTHY	\N	2026-08-19 18:20:44.759058
2943	backup	UNAVAILABLE	\N	2026-08-19 18:20:44.759058
2944	sentry	NOT_CONFIGURED	\N	2026-08-19 18:20:44.759058
2945	openai	NOT_CONFIGURED	\N	2026-08-19 18:20:44.759058
2946	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:20:44.759058
2947	simulation	HEALTHY	\N	2026-08-19 18:20:44.759058
2948	application	HEALTHY	4.5	2026-08-19 18:20:44.759058
2014	database	HEALTHY	1	2026-08-19 17:14:56.049366
2015	redis	NOT_CONFIGURED	\N	2026-08-19 17:14:56.049366
2016	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:14:56.049366
2017	celery	NOT_CONFIGURED	\N	2026-08-19 17:14:56.049366
2018	email	HEALTHY	\N	2026-08-19 17:14:56.049366
2019	backup	UNAVAILABLE	\N	2026-08-19 17:14:56.049366
2020	sentry	NOT_CONFIGURED	\N	2026-08-19 17:14:56.049366
2021	openai	NOT_CONFIGURED	\N	2026-08-19 17:14:56.049366
2022	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:14:56.049366
2023	simulation	HEALTHY	\N	2026-08-19 17:14:56.049366
2024	application	HEALTHY	4.5	2026-08-19 17:14:56.049366
2025	database	HEALTHY	0	2026-08-19 17:15:26.077115
2026	redis	NOT_CONFIGURED	\N	2026-08-19 17:15:26.077115
2027	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:15:26.077115
2028	celery	NOT_CONFIGURED	\N	2026-08-19 17:15:26.077115
2029	email	HEALTHY	\N	2026-08-19 17:15:26.077115
2030	backup	UNAVAILABLE	\N	2026-08-19 17:15:26.077115
2031	sentry	NOT_CONFIGURED	\N	2026-08-19 17:15:26.077115
2032	openai	NOT_CONFIGURED	\N	2026-08-19 17:15:26.077115
2033	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:15:26.077115
2034	simulation	HEALTHY	\N	2026-08-19 17:15:26.077115
2035	application	HEALTHY	4.5	2026-08-19 17:15:26.077115
2036	database	HEALTHY	0.96	2026-08-19 17:15:56.167661
2037	redis	NOT_CONFIGURED	\N	2026-08-19 17:15:56.167661
2038	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:15:56.167661
2039	celery	NOT_CONFIGURED	\N	2026-08-19 17:15:56.167661
2040	email	HEALTHY	\N	2026-08-19 17:15:56.167661
2041	backup	UNAVAILABLE	\N	2026-08-19 17:15:56.167661
2042	sentry	NOT_CONFIGURED	\N	2026-08-19 17:15:56.167661
2043	openai	NOT_CONFIGURED	\N	2026-08-19 17:15:56.167661
2044	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:15:56.167661
2045	simulation	HEALTHY	\N	2026-08-19 17:15:56.167661
2046	application	HEALTHY	4.5	2026-08-19 17:15:56.167661
2080	database	HEALTHY	0	2026-08-19 17:17:56.344446
2081	redis	NOT_CONFIGURED	\N	2026-08-19 17:17:56.344446
2082	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:17:56.344446
2083	celery	NOT_CONFIGURED	\N	2026-08-19 17:17:56.344446
2084	email	HEALTHY	\N	2026-08-19 17:17:56.344446
2085	backup	UNAVAILABLE	\N	2026-08-19 17:17:56.344446
2086	sentry	NOT_CONFIGURED	\N	2026-08-19 17:17:56.344446
2087	openai	NOT_CONFIGURED	\N	2026-08-19 17:17:56.345442
2088	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:17:56.345442
2089	simulation	HEALTHY	\N	2026-08-19 17:17:56.345442
2090	application	HEALTHY	4.5	2026-08-19 17:17:56.345442
2113	database	HEALTHY	1	2026-08-19 17:19:26.448016
2114	redis	NOT_CONFIGURED	\N	2026-08-19 17:19:26.449055
2115	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:19:26.449055
2116	celery	NOT_CONFIGURED	\N	2026-08-19 17:19:26.449055
2117	email	HEALTHY	\N	2026-08-19 17:19:26.449055
2118	backup	UNAVAILABLE	\N	2026-08-19 17:19:26.449055
2119	sentry	NOT_CONFIGURED	\N	2026-08-19 17:19:26.449055
2120	openai	NOT_CONFIGURED	\N	2026-08-19 17:19:26.449055
2121	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:19:26.449055
2122	simulation	HEALTHY	\N	2026-08-19 17:19:26.449055
2123	application	HEALTHY	4.5	2026-08-19 17:19:26.449055
2124	database	HEALTHY	0	2026-08-19 17:19:56.479634
2125	redis	NOT_CONFIGURED	\N	2026-08-19 17:19:56.479634
2126	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:19:56.479634
2127	celery	NOT_CONFIGURED	\N	2026-08-19 17:19:56.479634
2128	email	HEALTHY	\N	2026-08-19 17:19:56.479634
2129	backup	UNAVAILABLE	\N	2026-08-19 17:19:56.479634
2130	sentry	NOT_CONFIGURED	\N	2026-08-19 17:19:56.479634
2131	openai	NOT_CONFIGURED	\N	2026-08-19 17:19:56.480636
2132	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:19:56.480636
2133	simulation	HEALTHY	\N	2026-08-19 17:19:56.480636
2134	application	HEALTHY	4.5	2026-08-19 17:19:56.480636
2828	database	HEALTHY	0	2026-08-19 18:17:14.488657
2829	redis	NOT_CONFIGURED	\N	2026-08-19 18:17:14.488657
2830	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:17:14.488657
2831	celery	NOT_CONFIGURED	\N	2026-08-19 18:17:14.488657
2832	email	HEALTHY	\N	2026-08-19 18:17:14.488657
2833	backup	UNAVAILABLE	\N	2026-08-19 18:17:14.488657
2834	sentry	NOT_CONFIGURED	\N	2026-08-19 18:17:14.488657
2835	openai	NOT_CONFIGURED	\N	2026-08-19 18:17:14.488657
2836	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:17:14.488657
2837	simulation	HEALTHY	\N	2026-08-19 18:17:14.488657
2838	application	HEALTHY	4.5	2026-08-19 18:17:14.488657
2960	database	HEALTHY	0	2026-08-19 18:21:14.785098
2961	redis	NOT_CONFIGURED	\N	2026-08-19 18:21:14.785098
2962	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:21:14.785098
2963	celery	NOT_CONFIGURED	\N	2026-08-19 18:21:14.785098
2964	email	HEALTHY	\N	2026-08-19 18:21:14.785098
2965	backup	UNAVAILABLE	\N	2026-08-19 18:21:14.785098
2966	sentry	NOT_CONFIGURED	\N	2026-08-19 18:21:14.785098
2967	openai	NOT_CONFIGURED	\N	2026-08-19 18:21:14.785098
2968	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:21:14.785098
2969	simulation	HEALTHY	\N	2026-08-19 18:21:14.785098
2970	application	HEALTHY	4.5	2026-08-19 18:21:14.785098
2102	database	HEALTHY	1	2026-08-19 17:18:56.413112
2103	redis	NOT_CONFIGURED	\N	2026-08-19 17:18:56.414112
2104	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:18:56.414112
2105	celery	NOT_CONFIGURED	\N	2026-08-19 17:18:56.414112
2106	email	HEALTHY	\N	2026-08-19 17:18:56.414112
2107	backup	UNAVAILABLE	\N	2026-08-19 17:18:56.414112
2108	sentry	NOT_CONFIGURED	\N	2026-08-19 17:18:56.414112
2109	openai	NOT_CONFIGURED	\N	2026-08-19 17:18:56.414112
2110	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:18:56.414112
2111	simulation	HEALTHY	\N	2026-08-19 17:18:56.414112
2112	application	HEALTHY	4.5	2026-08-19 17:18:56.414112
2135	database	HEALTHY	1	2026-08-19 17:20:26.50915
2136	redis	NOT_CONFIGURED	\N	2026-08-19 17:20:26.50915
2137	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:20:26.50915
2138	celery	NOT_CONFIGURED	\N	2026-08-19 17:20:26.50915
2139	email	HEALTHY	\N	2026-08-19 17:20:26.50915
2140	backup	UNAVAILABLE	\N	2026-08-19 17:20:26.50915
2141	sentry	NOT_CONFIGURED	\N	2026-08-19 17:20:26.50915
2142	openai	NOT_CONFIGURED	\N	2026-08-19 17:20:26.50915
2143	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:20:26.50915
2144	simulation	HEALTHY	\N	2026-08-19 17:20:26.50915
2145	application	HEALTHY	4.5	2026-08-19 17:20:26.510152
2146	database	HEALTHY	0	2026-08-19 17:20:56.545429
2147	redis	NOT_CONFIGURED	\N	2026-08-19 17:20:56.545429
2148	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:20:56.545429
2149	celery	NOT_CONFIGURED	\N	2026-08-19 17:20:56.545429
2150	email	HEALTHY	\N	2026-08-19 17:20:56.545429
2151	backup	UNAVAILABLE	\N	2026-08-19 17:20:56.545429
2152	sentry	NOT_CONFIGURED	\N	2026-08-19 17:20:56.545429
2153	openai	NOT_CONFIGURED	\N	2026-08-19 17:20:56.545429
2154	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:20:56.545429
2155	simulation	HEALTHY	\N	2026-08-19 17:20:56.545429
2156	application	HEALTHY	4.5	2026-08-19 17:20:56.545429
2157	database	HEALTHY	1.99	2026-08-19 17:21:26.621726
2158	redis	NOT_CONFIGURED	\N	2026-08-19 17:21:26.621726
2159	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:21:26.621726
2160	celery	NOT_CONFIGURED	\N	2026-08-19 17:21:26.621726
2161	email	HEALTHY	\N	2026-08-19 17:21:26.621726
2162	backup	UNAVAILABLE	\N	2026-08-19 17:21:26.621726
2163	sentry	NOT_CONFIGURED	\N	2026-08-19 17:21:26.621726
2164	openai	NOT_CONFIGURED	\N	2026-08-19 17:21:26.621726
2165	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:21:26.621726
2166	simulation	HEALTHY	\N	2026-08-19 17:21:26.623365
2167	application	HEALTHY	4.5	2026-08-19 17:21:26.623365
2168	database	HEALTHY	0.95	2026-08-19 17:21:56.690583
2169	redis	NOT_CONFIGURED	\N	2026-08-19 17:21:56.690583
2170	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:21:56.690583
2171	celery	NOT_CONFIGURED	\N	2026-08-19 17:21:56.690583
2172	email	HEALTHY	\N	2026-08-19 17:21:56.690583
2173	backup	UNAVAILABLE	\N	2026-08-19 17:21:56.690583
2174	sentry	NOT_CONFIGURED	\N	2026-08-19 17:21:56.690583
2175	openai	NOT_CONFIGURED	\N	2026-08-19 17:21:56.690583
2176	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:21:56.690583
2177	simulation	HEALTHY	\N	2026-08-19 17:21:56.690583
2178	application	HEALTHY	4.5	2026-08-19 17:21:56.691599
2179	database	HEALTHY	0	2026-08-19 17:22:26.735083
2180	redis	NOT_CONFIGURED	\N	2026-08-19 17:22:26.735083
2181	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:22:26.735083
2182	celery	NOT_CONFIGURED	\N	2026-08-19 17:22:26.735083
2183	email	HEALTHY	\N	2026-08-19 17:22:26.735083
2184	backup	UNAVAILABLE	\N	2026-08-19 17:22:26.735083
2185	sentry	NOT_CONFIGURED	\N	2026-08-19 17:22:26.735083
2186	openai	NOT_CONFIGURED	\N	2026-08-19 17:22:26.735083
2187	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:22:26.735083
2188	simulation	HEALTHY	\N	2026-08-19 17:22:26.735083
2189	application	HEALTHY	4.5	2026-08-19 17:22:26.735083
2190	database	HEALTHY	0	2026-08-19 17:22:56.766909
2191	redis	NOT_CONFIGURED	\N	2026-08-19 17:22:56.766909
2192	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:22:56.766909
2193	celery	NOT_CONFIGURED	\N	2026-08-19 17:22:56.766909
2194	email	HEALTHY	\N	2026-08-19 17:22:56.766909
2195	backup	UNAVAILABLE	\N	2026-08-19 17:22:56.766909
2196	sentry	NOT_CONFIGURED	\N	2026-08-19 17:22:56.766909
2197	openai	NOT_CONFIGURED	\N	2026-08-19 17:22:56.766909
2198	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:22:56.766909
2199	simulation	HEALTHY	\N	2026-08-19 17:22:56.766909
2200	application	HEALTHY	4.5	2026-08-19 17:22:56.766909
2201	database	HEALTHY	0	2026-08-19 17:23:26.808649
2202	redis	NOT_CONFIGURED	\N	2026-08-19 17:23:26.808649
2203	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:23:26.808649
2204	celery	NOT_CONFIGURED	\N	2026-08-19 17:23:26.808649
2205	email	HEALTHY	\N	2026-08-19 17:23:26.808649
2206	backup	UNAVAILABLE	\N	2026-08-19 17:23:26.808649
2207	sentry	NOT_CONFIGURED	\N	2026-08-19 17:23:26.808649
2208	openai	NOT_CONFIGURED	\N	2026-08-19 17:23:26.808649
2209	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:23:26.809651
2210	simulation	HEALTHY	\N	2026-08-19 17:23:26.809651
2211	application	HEALTHY	4.5	2026-08-19 17:23:26.809651
2212	database	HEALTHY	1	2026-08-19 17:23:56.848013
2213	redis	NOT_CONFIGURED	\N	2026-08-19 17:23:56.848013
2214	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:23:56.849295
2215	celery	NOT_CONFIGURED	\N	2026-08-19 17:23:56.849295
2216	email	HEALTHY	\N	2026-08-19 17:23:56.849295
2217	backup	UNAVAILABLE	\N	2026-08-19 17:23:56.849295
2218	sentry	NOT_CONFIGURED	\N	2026-08-19 17:23:56.849295
2219	openai	NOT_CONFIGURED	\N	2026-08-19 17:23:56.849295
2220	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:23:56.849295
2221	simulation	HEALTHY	\N	2026-08-19 17:23:56.849295
2222	application	HEALTHY	4.5	2026-08-19 17:23:56.849295
2223	database	HEALTHY	1.05	2026-08-19 17:24:26.879047
2224	redis	NOT_CONFIGURED	\N	2026-08-19 17:24:26.880047
2225	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:24:26.880047
2226	celery	NOT_CONFIGURED	\N	2026-08-19 17:24:26.880047
2227	email	HEALTHY	\N	2026-08-19 17:24:26.880047
2228	backup	UNAVAILABLE	\N	2026-08-19 17:24:26.880047
2229	sentry	NOT_CONFIGURED	\N	2026-08-19 17:24:26.880047
2230	openai	NOT_CONFIGURED	\N	2026-08-19 17:24:26.880047
2231	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:24:26.880047
2232	simulation	HEALTHY	\N	2026-08-19 17:24:26.880047
2233	application	HEALTHY	4.5	2026-08-19 17:24:26.880047
2234	database	HEALTHY	1	2026-08-19 17:24:56.918597
2235	redis	NOT_CONFIGURED	\N	2026-08-19 17:24:56.918597
2236	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:24:56.918597
2237	celery	NOT_CONFIGURED	\N	2026-08-19 17:24:56.918597
2238	email	HEALTHY	\N	2026-08-19 17:24:56.918597
2239	backup	UNAVAILABLE	\N	2026-08-19 17:24:56.918597
2240	sentry	NOT_CONFIGURED	\N	2026-08-19 17:24:56.918597
2241	openai	NOT_CONFIGURED	\N	2026-08-19 17:24:56.918597
2242	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:24:56.918597
2243	simulation	HEALTHY	\N	2026-08-19 17:24:56.918597
2244	application	HEALTHY	4.5	2026-08-19 17:24:56.918597
2245	database	HEALTHY	0	2026-08-19 17:25:26.950968
2246	redis	NOT_CONFIGURED	\N	2026-08-19 17:25:26.950968
2247	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:25:26.950968
2248	celery	NOT_CONFIGURED	\N	2026-08-19 17:25:26.950968
2249	email	HEALTHY	\N	2026-08-19 17:25:26.950968
2250	backup	UNAVAILABLE	\N	2026-08-19 17:25:26.950968
2251	sentry	NOT_CONFIGURED	\N	2026-08-19 17:25:26.950968
2252	openai	NOT_CONFIGURED	\N	2026-08-19 17:25:26.950968
2253	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:25:26.950968
2254	simulation	HEALTHY	\N	2026-08-19 17:25:26.950968
2255	application	HEALTHY	4.5	2026-08-19 17:25:26.950968
2256	database	HEALTHY	1	2026-08-19 17:25:56.983312
2257	redis	NOT_CONFIGURED	\N	2026-08-19 17:25:56.983312
2258	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:25:56.984315
2259	celery	NOT_CONFIGURED	\N	2026-08-19 17:25:56.984315
2260	email	HEALTHY	\N	2026-08-19 17:25:56.984315
2261	backup	UNAVAILABLE	\N	2026-08-19 17:25:56.984315
2262	sentry	NOT_CONFIGURED	\N	2026-08-19 17:25:56.984315
2263	openai	NOT_CONFIGURED	\N	2026-08-19 17:25:56.984315
2264	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:25:56.984315
2265	simulation	HEALTHY	\N	2026-08-19 17:25:56.984315
2266	application	HEALTHY	4.5	2026-08-19 17:25:56.984315
2850	database	HEALTHY	1	2026-08-19 18:18:14.612283
2851	redis	NOT_CONFIGURED	\N	2026-08-19 18:18:14.612283
2852	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:18:14.612283
2853	celery	NOT_CONFIGURED	\N	2026-08-19 18:18:14.612283
2854	email	HEALTHY	\N	2026-08-19 18:18:14.612283
2855	backup	UNAVAILABLE	\N	2026-08-19 18:18:14.612283
2856	sentry	NOT_CONFIGURED	\N	2026-08-19 18:18:14.612283
2857	openai	NOT_CONFIGURED	\N	2026-08-19 18:18:14.612283
2858	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:18:14.612283
2859	simulation	HEALTHY	\N	2026-08-19 18:18:14.613285
2860	application	HEALTHY	4.5	2026-08-19 18:18:14.613285
2982	database	HEALTHY	1	2026-08-19 18:21:44.806761
2983	redis	NOT_CONFIGURED	\N	2026-08-19 18:21:44.806761
2984	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:21:44.806761
2985	celery	NOT_CONFIGURED	\N	2026-08-19 18:21:44.806761
2986	email	HEALTHY	\N	2026-08-19 18:21:44.806761
2987	backup	UNAVAILABLE	\N	2026-08-19 18:21:44.806761
2988	sentry	NOT_CONFIGURED	\N	2026-08-19 18:21:44.806761
2989	openai	NOT_CONFIGURED	\N	2026-08-19 18:21:44.806761
2990	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:21:44.807422
2991	simulation	HEALTHY	\N	2026-08-19 18:21:44.807422
2992	application	HEALTHY	4.5	2026-08-19 18:21:44.807422
2267	database	HEALTHY	0	2026-08-19 17:26:27.022829
2268	redis	NOT_CONFIGURED	\N	2026-08-19 17:26:27.022829
2269	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:26:27.022829
2270	celery	NOT_CONFIGURED	\N	2026-08-19 17:26:27.023818
2271	email	HEALTHY	\N	2026-08-19 17:26:27.023818
2272	backup	UNAVAILABLE	\N	2026-08-19 17:26:27.023818
2273	sentry	NOT_CONFIGURED	\N	2026-08-19 17:26:27.023818
2274	openai	NOT_CONFIGURED	\N	2026-08-19 17:26:27.023818
2275	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:26:27.023818
2276	simulation	HEALTHY	\N	2026-08-19 17:26:27.023818
2277	application	HEALTHY	4.5	2026-08-19 17:26:27.023818
2872	database	HEALTHY	0	2026-08-19 18:19:14.677312
2873	redis	NOT_CONFIGURED	\N	2026-08-19 18:19:14.677312
2874	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:19:14.677312
2875	celery	NOT_CONFIGURED	\N	2026-08-19 18:19:14.677312
2876	email	HEALTHY	\N	2026-08-19 18:19:14.677312
2877	backup	UNAVAILABLE	\N	2026-08-19 18:19:14.677312
2878	sentry	NOT_CONFIGURED	\N	2026-08-19 18:19:14.677312
2879	openai	NOT_CONFIGURED	\N	2026-08-19 18:19:14.677312
2880	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:19:14.677312
2881	simulation	HEALTHY	\N	2026-08-19 18:19:14.677312
2882	application	HEALTHY	4.5	2026-08-19 18:19:14.677312
3026	database	HEALTHY	0	2026-08-19 18:22:44.860035
3027	redis	NOT_CONFIGURED	\N	2026-08-19 18:22:44.860035
3028	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:22:44.860035
3029	celery	NOT_CONFIGURED	\N	2026-08-19 18:22:44.860035
3030	email	HEALTHY	\N	2026-08-19 18:22:44.860035
3031	backup	UNAVAILABLE	\N	2026-08-19 18:22:44.860035
3032	sentry	NOT_CONFIGURED	\N	2026-08-19 18:22:44.860035
3033	openai	NOT_CONFIGURED	\N	2026-08-19 18:22:44.860035
3034	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:22:44.860035
3035	simulation	HEALTHY	\N	2026-08-19 18:22:44.860035
3036	application	HEALTHY	4.5	2026-08-19 18:22:44.860035
2278	database	HEALTHY	0	2026-08-19 17:26:57.054833
2279	redis	NOT_CONFIGURED	\N	2026-08-19 17:26:57.054833
2280	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:26:57.054833
2281	celery	NOT_CONFIGURED	\N	2026-08-19 17:26:57.054833
2282	email	HEALTHY	\N	2026-08-19 17:26:57.054833
2283	backup	UNAVAILABLE	\N	2026-08-19 17:26:57.054833
2284	sentry	NOT_CONFIGURED	\N	2026-08-19 17:26:57.055832
2285	openai	NOT_CONFIGURED	\N	2026-08-19 17:26:57.055832
2286	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:26:57.055832
2287	simulation	HEALTHY	\N	2026-08-19 17:26:57.055832
2288	application	HEALTHY	4.5	2026-08-19 17:26:57.055832
2289	database	HEALTHY	1.37	2026-08-19 17:27:27.103673
2290	redis	NOT_CONFIGURED	\N	2026-08-19 17:27:27.103673
2291	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:27:27.103673
2292	celery	NOT_CONFIGURED	\N	2026-08-19 17:27:27.103673
2293	email	HEALTHY	\N	2026-08-19 17:27:27.103673
2294	backup	UNAVAILABLE	\N	2026-08-19 17:27:27.103673
2295	sentry	NOT_CONFIGURED	\N	2026-08-19 17:27:27.103673
2296	openai	NOT_CONFIGURED	\N	2026-08-19 17:27:27.103673
2297	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:27:27.103673
2298	simulation	HEALTHY	\N	2026-08-19 17:27:27.103673
2299	application	HEALTHY	4.5	2026-08-19 17:27:27.103673
2300	database	HEALTHY	2.02	2026-08-19 17:27:57.169766
2301	redis	NOT_CONFIGURED	\N	2026-08-19 17:27:57.169766
2302	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:27:57.169766
2303	celery	NOT_CONFIGURED	\N	2026-08-19 17:27:57.169766
2304	email	HEALTHY	\N	2026-08-19 17:27:57.169766
2305	backup	UNAVAILABLE	\N	2026-08-19 17:27:57.169766
2306	sentry	NOT_CONFIGURED	\N	2026-08-19 17:27:57.169766
2307	openai	NOT_CONFIGURED	\N	2026-08-19 17:27:57.169766
2308	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:27:57.169766
2309	simulation	HEALTHY	\N	2026-08-19 17:27:57.169766
2310	application	HEALTHY	4.5	2026-08-19 17:27:57.169766
2344	database	HEALTHY	0	2026-08-19 17:29:57.346478
2345	redis	NOT_CONFIGURED	\N	2026-08-19 17:29:57.346478
2346	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:29:57.346478
2347	celery	NOT_CONFIGURED	\N	2026-08-19 17:29:57.346478
2348	email	HEALTHY	\N	2026-08-19 17:29:57.346478
2349	backup	UNAVAILABLE	\N	2026-08-19 17:29:57.346478
2350	sentry	NOT_CONFIGURED	\N	2026-08-19 17:29:57.346478
2351	openai	NOT_CONFIGURED	\N	2026-08-19 17:29:57.346478
2352	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:29:57.346478
2353	simulation	HEALTHY	\N	2026-08-19 17:29:57.346478
2354	application	HEALTHY	4.5	2026-08-19 17:29:57.346478
2366	database	HEALTHY	1	2026-08-19 17:30:57.403266
2367	redis	NOT_CONFIGURED	\N	2026-08-19 17:30:57.404307
2368	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:30:57.404307
2369	celery	NOT_CONFIGURED	\N	2026-08-19 17:30:57.404307
2370	email	HEALTHY	\N	2026-08-19 17:30:57.404307
2371	backup	UNAVAILABLE	\N	2026-08-19 17:30:57.404307
2372	sentry	NOT_CONFIGURED	\N	2026-08-19 17:30:57.404307
2373	openai	NOT_CONFIGURED	\N	2026-08-19 17:30:57.404307
2374	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:30:57.404307
2375	simulation	HEALTHY	\N	2026-08-19 17:30:57.404307
2376	application	HEALTHY	4.5	2026-08-19 17:30:57.404307
2883	database	HEALTHY	0	2026-08-19 18:19:23.320233
2884	redis	NOT_CONFIGURED	\N	2026-08-19 18:19:23.320233
2885	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:19:23.320233
2886	celery	NOT_CONFIGURED	\N	2026-08-19 18:19:23.320233
2887	email	HEALTHY	\N	2026-08-19 18:19:23.321235
2888	backup	HEALTHY	\N	2026-08-19 18:19:23.321235
2889	sentry	NOT_CONFIGURED	\N	2026-08-19 18:19:23.321235
2890	openai	NOT_CONFIGURED	\N	2026-08-19 18:19:23.321235
2891	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:19:23.321235
2892	simulation	HEALTHY	\N	2026-08-19 18:19:23.321235
2893	application	HEALTHY	4.5	2026-08-19 18:19:23.321235
2311	database	HEALTHY	1	2026-08-19 17:28:27.211457
2312	redis	NOT_CONFIGURED	\N	2026-08-19 17:28:27.212453
2313	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:28:27.212453
2314	celery	NOT_CONFIGURED	\N	2026-08-19 17:28:27.212453
2315	email	HEALTHY	\N	2026-08-19 17:28:27.212453
2316	backup	UNAVAILABLE	\N	2026-08-19 17:28:27.212453
2317	sentry	NOT_CONFIGURED	\N	2026-08-19 17:28:27.212453
2318	openai	NOT_CONFIGURED	\N	2026-08-19 17:28:27.212453
2319	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:28:27.212453
2320	simulation	HEALTHY	\N	2026-08-19 17:28:27.212453
2321	application	HEALTHY	4.5	2026-08-19 17:28:27.212453
2322	database	HEALTHY	1.02	2026-08-19 17:28:57.260897
2323	redis	NOT_CONFIGURED	\N	2026-08-19 17:28:57.260897
2324	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:28:57.260897
2325	celery	NOT_CONFIGURED	\N	2026-08-19 17:28:57.260897
2326	email	HEALTHY	\N	2026-08-19 17:28:57.260897
2327	backup	UNAVAILABLE	\N	2026-08-19 17:28:57.260897
2328	sentry	NOT_CONFIGURED	\N	2026-08-19 17:28:57.260897
2329	openai	NOT_CONFIGURED	\N	2026-08-19 17:28:57.260897
2330	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:28:57.260897
2331	simulation	HEALTHY	\N	2026-08-19 17:28:57.260897
2332	application	HEALTHY	4.5	2026-08-19 17:28:57.260897
2333	database	HEALTHY	0.99	2026-08-19 17:29:27.314667
2334	redis	NOT_CONFIGURED	\N	2026-08-19 17:29:27.314667
2335	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:29:27.314667
2336	celery	NOT_CONFIGURED	\N	2026-08-19 17:29:27.314667
2337	email	HEALTHY	\N	2026-08-19 17:29:27.314667
2338	backup	UNAVAILABLE	\N	2026-08-19 17:29:27.315669
2339	sentry	NOT_CONFIGURED	\N	2026-08-19 17:29:27.315669
2340	openai	NOT_CONFIGURED	\N	2026-08-19 17:29:27.315669
2341	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:29:27.315669
2342	simulation	HEALTHY	\N	2026-08-19 17:29:27.315669
2343	application	HEALTHY	4.5	2026-08-19 17:29:27.315669
2377	database	HEALTHY	1	2026-08-19 17:31:27.440109
2378	redis	NOT_CONFIGURED	\N	2026-08-19 17:31:27.440109
2379	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:31:27.441127
2380	celery	NOT_CONFIGURED	\N	2026-08-19 17:31:27.441127
2381	email	HEALTHY	\N	2026-08-19 17:31:27.441127
2382	backup	UNAVAILABLE	\N	2026-08-19 17:31:27.441127
2383	sentry	NOT_CONFIGURED	\N	2026-08-19 17:31:27.441127
2384	openai	NOT_CONFIGURED	\N	2026-08-19 17:31:27.441127
2385	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:31:27.441127
2386	simulation	HEALTHY	\N	2026-08-19 17:31:27.441127
2387	application	HEALTHY	4.5	2026-08-19 17:31:27.441127
2388	database	HEALTHY	1	2026-08-19 17:31:57.466346
2389	redis	NOT_CONFIGURED	\N	2026-08-19 17:31:57.466346
2390	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:31:57.467337
2391	celery	NOT_CONFIGURED	\N	2026-08-19 17:31:57.467337
2392	email	HEALTHY	\N	2026-08-19 17:31:57.467337
2393	backup	UNAVAILABLE	\N	2026-08-19 17:31:57.467337
2394	sentry	NOT_CONFIGURED	\N	2026-08-19 17:31:57.467337
2395	openai	NOT_CONFIGURED	\N	2026-08-19 17:31:57.467337
2396	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:31:57.467826
2397	simulation	HEALTHY	\N	2026-08-19 17:31:57.467826
2398	application	HEALTHY	4.5	2026-08-19 17:31:57.467826
2894	database	HEALTHY	0	2026-08-19 18:19:44.706697
2895	redis	NOT_CONFIGURED	\N	2026-08-19 18:19:44.706697
2896	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:19:44.707697
2897	celery	NOT_CONFIGURED	\N	2026-08-19 18:19:44.707697
2898	email	HEALTHY	\N	2026-08-19 18:19:44.707697
2899	backup	DEGRADED	\N	2026-08-19 18:19:44.707697
2900	sentry	NOT_CONFIGURED	\N	2026-08-19 18:19:44.707697
2901	openai	NOT_CONFIGURED	\N	2026-08-19 18:19:44.707697
2902	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:19:44.707697
2903	simulation	HEALTHY	\N	2026-08-19 18:19:44.707697
2904	application	HEALTHY	4.5	2026-08-19 18:19:44.707697
3048	database	HEALTHY	1	2026-08-19 18:23:14.89588
3049	redis	NOT_CONFIGURED	\N	2026-08-19 18:23:14.89588
3050	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:23:14.89588
3051	celery	NOT_CONFIGURED	\N	2026-08-19 18:23:14.89588
3052	email	HEALTHY	\N	2026-08-19 18:23:14.89588
3053	backup	UNAVAILABLE	\N	2026-08-19 18:23:14.89588
3054	sentry	NOT_CONFIGURED	\N	2026-08-19 18:23:14.896879
3055	openai	NOT_CONFIGURED	\N	2026-08-19 18:23:14.896879
3056	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:23:14.896879
3057	simulation	HEALTHY	\N	2026-08-19 18:23:14.896879
3058	application	HEALTHY	4.5	2026-08-19 18:23:14.896879
2355	database	HEALTHY	1.01	2026-08-19 17:30:27.373681
2356	redis	NOT_CONFIGURED	\N	2026-08-19 17:30:27.373681
2357	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:30:27.373681
2358	celery	NOT_CONFIGURED	\N	2026-08-19 17:30:27.373681
2359	email	HEALTHY	\N	2026-08-19 17:30:27.373681
2360	backup	UNAVAILABLE	\N	2026-08-19 17:30:27.373681
2361	sentry	NOT_CONFIGURED	\N	2026-08-19 17:30:27.373681
2362	openai	NOT_CONFIGURED	\N	2026-08-19 17:30:27.373681
2363	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:30:27.373681
2364	simulation	HEALTHY	\N	2026-08-19 17:30:27.373681
2365	application	HEALTHY	4.5	2026-08-19 17:30:27.373681
2399	database	HEALTHY	0	2026-08-19 17:32:27.491365
2400	redis	NOT_CONFIGURED	\N	2026-08-19 17:32:27.492366
2401	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:32:27.492366
2402	celery	NOT_CONFIGURED	\N	2026-08-19 17:32:27.492366
2403	email	HEALTHY	\N	2026-08-19 17:32:27.492366
2404	backup	UNAVAILABLE	\N	2026-08-19 17:32:27.492366
2405	sentry	NOT_CONFIGURED	\N	2026-08-19 17:32:27.492366
2406	openai	NOT_CONFIGURED	\N	2026-08-19 17:32:27.492366
2407	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:32:27.492366
2408	simulation	HEALTHY	\N	2026-08-19 17:32:27.492366
2409	application	HEALTHY	4.5	2026-08-19 17:32:27.492366
2410	database	HEALTHY	0	2026-08-19 17:32:57.531701
2411	redis	NOT_CONFIGURED	\N	2026-08-19 17:32:57.531701
2412	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:32:57.531701
2413	celery	NOT_CONFIGURED	\N	2026-08-19 17:32:57.531701
2414	email	HEALTHY	\N	2026-08-19 17:32:57.531701
2415	backup	UNAVAILABLE	\N	2026-08-19 17:32:57.532697
2416	sentry	NOT_CONFIGURED	\N	2026-08-19 17:32:57.532697
2417	openai	NOT_CONFIGURED	\N	2026-08-19 17:32:57.532697
2418	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:32:57.532697
2419	simulation	HEALTHY	\N	2026-08-19 17:32:57.532697
2420	application	HEALTHY	4.5	2026-08-19 17:32:57.532697
2421	database	HEALTHY	1	2026-08-19 17:33:27.564793
2422	redis	NOT_CONFIGURED	\N	2026-08-19 17:33:27.564793
2423	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:33:27.564793
2424	celery	NOT_CONFIGURED	\N	2026-08-19 17:33:27.564793
2425	email	HEALTHY	\N	2026-08-19 17:33:27.564793
2426	backup	UNAVAILABLE	\N	2026-08-19 17:33:27.564793
2427	sentry	NOT_CONFIGURED	\N	2026-08-19 17:33:27.564793
2428	openai	NOT_CONFIGURED	\N	2026-08-19 17:33:27.564793
2429	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:33:27.564793
2430	simulation	HEALTHY	\N	2026-08-19 17:33:27.564793
2431	application	HEALTHY	4.5	2026-08-19 17:33:27.565787
2432	database	HEALTHY	0	2026-08-19 17:33:57.596783
2433	redis	NOT_CONFIGURED	\N	2026-08-19 17:33:57.596783
2434	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:33:57.596783
2435	celery	NOT_CONFIGURED	\N	2026-08-19 17:33:57.596783
2436	email	HEALTHY	\N	2026-08-19 17:33:57.596783
2437	backup	UNAVAILABLE	\N	2026-08-19 17:33:57.596783
2438	sentry	NOT_CONFIGURED	\N	2026-08-19 17:33:57.596783
2439	openai	NOT_CONFIGURED	\N	2026-08-19 17:33:57.596783
2440	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:33:57.596783
2441	simulation	HEALTHY	\N	2026-08-19 17:33:57.596783
2442	application	HEALTHY	4.5	2026-08-19 17:33:57.596783
2443	database	HEALTHY	0	2026-08-19 17:34:27.650013
2444	redis	NOT_CONFIGURED	\N	2026-08-19 17:34:27.650013
2445	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:34:27.650013
2446	celery	NOT_CONFIGURED	\N	2026-08-19 17:34:27.650013
2447	email	HEALTHY	\N	2026-08-19 17:34:27.651012
2448	backup	UNAVAILABLE	\N	2026-08-19 17:34:27.651012
2449	sentry	NOT_CONFIGURED	\N	2026-08-19 17:34:27.651012
2450	openai	NOT_CONFIGURED	\N	2026-08-19 17:34:27.651012
2451	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:34:27.651012
2452	simulation	HEALTHY	\N	2026-08-19 17:34:27.651012
2453	application	HEALTHY	4.5	2026-08-19 17:34:27.651012
2454	database	HEALTHY	1.11	2026-08-19 17:34:57.714404
2455	redis	NOT_CONFIGURED	\N	2026-08-19 17:34:57.714404
2456	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:34:57.714404
2457	celery	NOT_CONFIGURED	\N	2026-08-19 17:34:57.714404
2458	email	HEALTHY	\N	2026-08-19 17:34:57.714404
2459	backup	UNAVAILABLE	\N	2026-08-19 17:34:57.714404
2460	sentry	NOT_CONFIGURED	\N	2026-08-19 17:34:57.714404
2461	openai	NOT_CONFIGURED	\N	2026-08-19 17:34:57.714404
2462	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:34:57.714404
2463	simulation	HEALTHY	\N	2026-08-19 17:34:57.714404
2464	application	HEALTHY	4.5	2026-08-19 17:34:57.714404
2465	database	HEALTHY	1	2026-08-19 17:35:27.773865
2466	redis	NOT_CONFIGURED	\N	2026-08-19 17:35:27.773865
2467	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:35:27.773865
2468	celery	NOT_CONFIGURED	\N	2026-08-19 17:35:27.773865
2469	email	HEALTHY	\N	2026-08-19 17:35:27.773865
2470	backup	UNAVAILABLE	\N	2026-08-19 17:35:27.773865
2471	sentry	NOT_CONFIGURED	\N	2026-08-19 17:35:27.773865
2472	openai	NOT_CONFIGURED	\N	2026-08-19 17:35:27.773865
2473	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:35:27.773865
2474	simulation	HEALTHY	\N	2026-08-19 17:35:27.773865
2475	application	HEALTHY	4.5	2026-08-19 17:35:27.773865
2476	database	HEALTHY	1.01	2026-08-19 17:35:57.808189
2477	redis	NOT_CONFIGURED	\N	2026-08-19 17:35:57.808189
2478	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:35:57.80919
2479	celery	NOT_CONFIGURED	\N	2026-08-19 17:35:57.80919
2480	email	HEALTHY	\N	2026-08-19 17:35:57.80919
2481	backup	UNAVAILABLE	\N	2026-08-19 17:35:57.80919
2482	sentry	NOT_CONFIGURED	\N	2026-08-19 17:35:57.80919
2483	openai	NOT_CONFIGURED	\N	2026-08-19 17:35:57.81019
2484	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:35:57.81019
2485	simulation	HEALTHY	\N	2026-08-19 17:35:57.81019
2486	application	HEALTHY	4.5	2026-08-19 17:35:57.81019
2487	database	HEALTHY	1	2026-08-19 17:36:27.83402
2488	redis	NOT_CONFIGURED	\N	2026-08-19 17:36:27.83402
2489	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:36:27.835025
2490	celery	NOT_CONFIGURED	\N	2026-08-19 17:36:27.835025
2491	email	HEALTHY	\N	2026-08-19 17:36:27.835025
2492	backup	UNAVAILABLE	\N	2026-08-19 17:36:27.835025
2493	sentry	NOT_CONFIGURED	\N	2026-08-19 17:36:27.835025
2494	openai	NOT_CONFIGURED	\N	2026-08-19 17:36:27.835025
2495	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:36:27.835025
2496	simulation	HEALTHY	\N	2026-08-19 17:36:27.835025
2497	application	HEALTHY	4.5	2026-08-19 17:36:27.835025
2498	database	HEALTHY	1.53	2026-08-19 17:36:57.871032
2499	redis	NOT_CONFIGURED	\N	2026-08-19 17:36:57.871032
2500	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:36:57.871032
2501	celery	NOT_CONFIGURED	\N	2026-08-19 17:36:57.871032
2502	email	HEALTHY	\N	2026-08-19 17:36:57.871032
2503	backup	UNAVAILABLE	\N	2026-08-19 17:36:57.871032
2504	sentry	NOT_CONFIGURED	\N	2026-08-19 17:36:57.871032
2505	openai	NOT_CONFIGURED	\N	2026-08-19 17:36:57.871032
2506	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:36:57.871032
2507	simulation	HEALTHY	\N	2026-08-19 17:36:57.871032
2508	application	HEALTHY	4.5	2026-08-19 17:36:57.871032
2509	database	HEALTHY	1	2026-08-19 17:37:27.902669
2510	redis	NOT_CONFIGURED	\N	2026-08-19 17:37:27.902669
2511	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:37:27.902669
2512	celery	NOT_CONFIGURED	\N	2026-08-19 17:37:27.902669
2513	email	HEALTHY	\N	2026-08-19 17:37:27.902669
2514	backup	UNAVAILABLE	\N	2026-08-19 17:37:27.902669
2515	sentry	NOT_CONFIGURED	\N	2026-08-19 17:37:27.902669
2516	openai	NOT_CONFIGURED	\N	2026-08-19 17:37:27.902669
2517	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:37:27.902669
2518	simulation	HEALTHY	\N	2026-08-19 17:37:27.903673
2519	application	HEALTHY	4.5	2026-08-19 17:37:27.903673
2520	database	HEALTHY	0	2026-08-19 17:37:57.944225
2521	redis	NOT_CONFIGURED	\N	2026-08-19 17:37:57.945225
2522	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:37:57.945225
2523	celery	NOT_CONFIGURED	\N	2026-08-19 17:37:57.945225
2524	email	HEALTHY	\N	2026-08-19 17:37:57.945225
2525	backup	UNAVAILABLE	\N	2026-08-19 17:37:57.945225
2526	sentry	NOT_CONFIGURED	\N	2026-08-19 17:37:57.945225
2527	openai	NOT_CONFIGURED	\N	2026-08-19 17:37:57.945225
2528	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:37:57.945225
2529	simulation	HEALTHY	\N	2026-08-19 17:37:57.945225
2530	application	HEALTHY	4.5	2026-08-19 17:37:57.945225
2905	database	HEALTHY	0.99	2026-08-19 18:19:53.354593
2906	redis	NOT_CONFIGURED	\N	2026-08-19 18:19:53.354593
2907	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:19:53.354593
2908	celery	NOT_CONFIGURED	\N	2026-08-19 18:19:53.354593
2909	email	HEALTHY	\N	2026-08-19 18:19:53.354593
2910	backup	DEGRADED	\N	2026-08-19 18:19:53.354593
2911	sentry	NOT_CONFIGURED	\N	2026-08-19 18:19:53.354593
2912	openai	NOT_CONFIGURED	\N	2026-08-19 18:19:53.354593
2913	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:19:53.354593
2914	simulation	HEALTHY	\N	2026-08-19 18:19:53.354593
2915	application	HEALTHY	4.5	2026-08-19 18:19:53.354593
2531	database	HEALTHY	0	2026-08-19 17:38:27.967346
2532	redis	NOT_CONFIGURED	\N	2026-08-19 17:38:27.967346
2533	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:38:27.967346
2534	celery	NOT_CONFIGURED	\N	2026-08-19 17:38:27.967346
2535	email	HEALTHY	\N	2026-08-19 17:38:27.967346
2536	backup	UNAVAILABLE	\N	2026-08-19 17:38:27.967346
2537	sentry	NOT_CONFIGURED	\N	2026-08-19 17:38:27.967346
2538	openai	NOT_CONFIGURED	\N	2026-08-19 17:38:27.967346
2539	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:38:27.967346
2540	simulation	HEALTHY	\N	2026-08-19 17:38:27.967346
2541	application	HEALTHY	4.5	2026-08-19 17:38:27.968347
2542	database	HEALTHY	1.98	2026-08-19 17:38:58.030375
2543	redis	NOT_CONFIGURED	\N	2026-08-19 17:38:58.030375
2544	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:38:58.030375
2545	celery	NOT_CONFIGURED	\N	2026-08-19 17:38:58.030375
2546	email	HEALTHY	\N	2026-08-19 17:38:58.031351
2547	backup	UNAVAILABLE	\N	2026-08-19 17:38:58.031351
2548	sentry	NOT_CONFIGURED	\N	2026-08-19 17:38:58.031351
2549	openai	NOT_CONFIGURED	\N	2026-08-19 17:38:58.031351
2550	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:38:58.031351
2551	simulation	HEALTHY	\N	2026-08-19 17:38:58.031351
2552	application	HEALTHY	4.5	2026-08-19 17:38:58.031351
2916	database	HEALTHY	0	2026-08-19 18:20:14.732593
2917	redis	NOT_CONFIGURED	\N	2026-08-19 18:20:14.733594
2918	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:20:14.733594
2919	celery	NOT_CONFIGURED	\N	2026-08-19 18:20:14.733594
2920	email	HEALTHY	\N	2026-08-19 18:20:14.733594
2921	backup	DEGRADED	\N	2026-08-19 18:20:14.733594
2922	sentry	NOT_CONFIGURED	\N	2026-08-19 18:20:14.733594
2923	openai	NOT_CONFIGURED	\N	2026-08-19 18:20:14.733594
2924	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:20:14.733594
2925	simulation	HEALTHY	\N	2026-08-19 18:20:14.733594
2926	application	HEALTHY	4.5	2026-08-19 18:20:14.733594
2553	database	HEALTHY	1.98	2026-08-19 17:39:28.098572
2554	redis	NOT_CONFIGURED	\N	2026-08-19 17:39:28.09958
2555	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:39:28.09958
2556	celery	NOT_CONFIGURED	\N	2026-08-19 17:39:28.09958
2557	email	HEALTHY	\N	2026-08-19 17:39:28.09958
2558	backup	UNAVAILABLE	\N	2026-08-19 17:39:28.09958
2559	sentry	NOT_CONFIGURED	\N	2026-08-19 17:39:28.09958
2560	openai	NOT_CONFIGURED	\N	2026-08-19 17:39:28.09958
2561	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:39:28.09958
2562	simulation	HEALTHY	\N	2026-08-19 17:39:28.09958
2563	application	HEALTHY	4.5	2026-08-19 17:39:28.09958
2564	database	HEALTHY	2.05	2026-08-19 17:39:58.159519
2565	redis	NOT_CONFIGURED	\N	2026-08-19 17:39:58.159519
2566	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:39:58.160514
2567	celery	NOT_CONFIGURED	\N	2026-08-19 17:39:58.160514
2568	email	HEALTHY	\N	2026-08-19 17:39:58.160514
2569	backup	UNAVAILABLE	\N	2026-08-19 17:39:58.160514
2570	sentry	NOT_CONFIGURED	\N	2026-08-19 17:39:58.160514
2571	openai	NOT_CONFIGURED	\N	2026-08-19 17:39:58.160514
2572	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:39:58.160514
2573	simulation	HEALTHY	\N	2026-08-19 17:39:58.160514
2574	application	HEALTHY	4.5	2026-08-19 17:39:58.160514
2927	database	HEALTHY	0	2026-08-19 18:20:23.392267
2928	redis	NOT_CONFIGURED	\N	2026-08-19 18:20:23.393267
2929	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:20:23.393267
2930	celery	NOT_CONFIGURED	\N	2026-08-19 18:20:23.393267
2931	email	HEALTHY	\N	2026-08-19 18:20:23.393267
2932	backup	UNAVAILABLE	\N	2026-08-19 18:20:23.393267
2933	sentry	NOT_CONFIGURED	\N	2026-08-19 18:20:23.393267
2934	openai	NOT_CONFIGURED	\N	2026-08-19 18:20:23.393267
2935	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:20:23.393267
2936	simulation	HEALTHY	\N	2026-08-19 18:20:23.393267
2937	application	HEALTHY	4.5	2026-08-19 18:20:23.393267
2949	database	HEALTHY	1.32	2026-08-19 18:20:53.414661
2950	redis	NOT_CONFIGURED	\N	2026-08-19 18:20:53.414661
2951	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:20:53.414661
2952	celery	NOT_CONFIGURED	\N	2026-08-19 18:20:53.414661
2953	email	HEALTHY	\N	2026-08-19 18:20:53.414661
2954	backup	UNAVAILABLE	\N	2026-08-19 18:20:53.414661
2955	sentry	NOT_CONFIGURED	\N	2026-08-19 18:20:53.414661
2956	openai	NOT_CONFIGURED	\N	2026-08-19 18:20:53.414661
2957	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:20:53.414661
2958	simulation	HEALTHY	\N	2026-08-19 18:20:53.414661
2959	application	HEALTHY	4.5	2026-08-19 18:20:53.414661
2993	database	HEALTHY	0.59	2026-08-19 18:21:53.566404
2994	redis	NOT_CONFIGURED	\N	2026-08-19 18:21:53.566404
2995	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:21:53.566404
2996	celery	NOT_CONFIGURED	\N	2026-08-19 18:21:53.566404
2997	email	HEALTHY	\N	2026-08-19 18:21:53.566404
2998	backup	UNAVAILABLE	\N	2026-08-19 18:21:53.566404
2999	sentry	NOT_CONFIGURED	\N	2026-08-19 18:21:53.566404
3000	openai	NOT_CONFIGURED	\N	2026-08-19 18:21:53.566404
3001	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:21:53.566404
3002	simulation	HEALTHY	\N	2026-08-19 18:21:53.566404
3003	application	HEALTHY	4.5	2026-08-19 18:21:53.566404
2575	database	HEALTHY	0.99	2026-08-19 17:40:28.243079
2576	redis	NOT_CONFIGURED	\N	2026-08-19 17:40:28.243079
2577	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:40:28.243079
2578	celery	NOT_CONFIGURED	\N	2026-08-19 17:40:28.243079
2579	email	HEALTHY	\N	2026-08-19 17:40:28.244076
2580	backup	UNAVAILABLE	\N	2026-08-19 17:40:28.244076
2581	sentry	NOT_CONFIGURED	\N	2026-08-19 17:40:28.244076
2582	openai	NOT_CONFIGURED	\N	2026-08-19 17:40:28.244076
2583	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:40:28.244076
2584	simulation	HEALTHY	\N	2026-08-19 17:40:28.244076
2585	application	HEALTHY	4.5	2026-08-19 17:40:28.244076
2971	database	HEALTHY	0	2026-08-19 18:21:23.527444
2972	redis	NOT_CONFIGURED	\N	2026-08-19 18:21:23.527444
2973	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:21:23.527444
2974	celery	NOT_CONFIGURED	\N	2026-08-19 18:21:23.527444
2975	email	HEALTHY	\N	2026-08-19 18:21:23.527444
2976	backup	UNAVAILABLE	\N	2026-08-19 18:21:23.527444
2977	sentry	NOT_CONFIGURED	\N	2026-08-19 18:21:23.527444
2978	openai	NOT_CONFIGURED	\N	2026-08-19 18:21:23.527444
2979	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:21:23.527444
2980	simulation	HEALTHY	\N	2026-08-19 18:21:23.527444
2981	application	HEALTHY	4.5	2026-08-19 18:21:23.527444
3015	database	HEALTHY	0	2026-08-19 18:22:23.59173
3016	redis	NOT_CONFIGURED	\N	2026-08-19 18:22:23.59173
3017	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:22:23.59173
3018	celery	NOT_CONFIGURED	\N	2026-08-19 18:22:23.59173
3019	email	HEALTHY	\N	2026-08-19 18:22:23.59173
3020	backup	UNAVAILABLE	\N	2026-08-19 18:22:23.59173
3021	sentry	NOT_CONFIGURED	\N	2026-08-19 18:22:23.59173
3022	openai	NOT_CONFIGURED	\N	2026-08-19 18:22:23.59173
3023	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:22:23.59173
3024	simulation	HEALTHY	\N	2026-08-19 18:22:23.59173
3025	application	HEALTHY	4.5	2026-08-19 18:22:23.59173
3037	database	HEALTHY	1.38	2026-08-19 18:22:53.650897
3038	redis	NOT_CONFIGURED	\N	2026-08-19 18:22:53.650897
3039	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:22:53.650897
3040	celery	NOT_CONFIGURED	\N	2026-08-19 18:22:53.650897
3041	email	HEALTHY	\N	2026-08-19 18:22:53.650897
3042	backup	UNAVAILABLE	\N	2026-08-19 18:22:53.650897
3043	sentry	NOT_CONFIGURED	\N	2026-08-19 18:22:53.650897
3044	openai	NOT_CONFIGURED	\N	2026-08-19 18:22:53.650897
3045	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:22:53.650897
3046	simulation	HEALTHY	\N	2026-08-19 18:22:53.650897
3047	application	HEALTHY	4.5	2026-08-19 18:22:53.651893
2586	database	HEALTHY	0	2026-08-19 17:40:58.284176
2587	redis	NOT_CONFIGURED	\N	2026-08-19 17:40:58.285177
2588	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:40:58.285177
2589	celery	NOT_CONFIGURED	\N	2026-08-19 17:40:58.285177
2590	email	HEALTHY	\N	2026-08-19 17:40:58.285177
2591	backup	UNAVAILABLE	\N	2026-08-19 17:40:58.285177
2592	sentry	NOT_CONFIGURED	\N	2026-08-19 17:40:58.285177
2593	openai	NOT_CONFIGURED	\N	2026-08-19 17:40:58.285177
2594	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:40:58.285177
2595	simulation	HEALTHY	\N	2026-08-19 17:40:58.285177
2596	application	HEALTHY	4.5	2026-08-19 17:40:58.285177
2597	database	HEALTHY	1	2026-08-19 18:03:54.409594
2598	redis	NOT_CONFIGURED	\N	2026-08-19 18:03:54.409594
2599	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:03:54.409594
2600	celery	NOT_CONFIGURED	\N	2026-08-19 18:03:54.409594
2601	email	HEALTHY	\N	2026-08-19 18:03:54.409594
2602	backup	UNAVAILABLE	\N	2026-08-19 18:03:54.409594
2603	sentry	NOT_CONFIGURED	\N	2026-08-19 18:03:54.41064
2604	openai	NOT_CONFIGURED	\N	2026-08-19 18:03:54.41064
2605	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:03:54.41064
2606	simulation	HEALTHY	\N	2026-08-19 18:03:54.41064
2607	application	HEALTHY	4.5	2026-08-19 18:03:54.41064
2608	database	HEALTHY	1	2026-08-19 18:06:56.751729
2609	redis	NOT_CONFIGURED	\N	2026-08-19 18:06:56.751729
2610	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:06:56.751729
2611	celery	NOT_CONFIGURED	\N	2026-08-19 18:06:56.751729
2612	email	HEALTHY	\N	2026-08-19 18:06:56.751729
2613	backup	UNAVAILABLE	\N	2026-08-19 18:06:56.751729
2614	sentry	NOT_CONFIGURED	\N	2026-08-19 18:06:56.751729
2615	openai	NOT_CONFIGURED	\N	2026-08-19 18:06:56.751729
2616	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:06:56.751729
2617	simulation	HEALTHY	\N	2026-08-19 18:06:56.751729
2618	application	HEALTHY	4.5	2026-08-19 18:06:56.751729
2619	database	HEALTHY	1.03	2026-08-19 18:07:26.79446
2620	redis	NOT_CONFIGURED	\N	2026-08-19 18:07:26.79446
2621	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:07:26.79446
2622	celery	NOT_CONFIGURED	\N	2026-08-19 18:07:26.79446
2623	email	HEALTHY	\N	2026-08-19 18:07:26.79446
2624	backup	UNAVAILABLE	\N	2026-08-19 18:07:26.79446
2625	sentry	NOT_CONFIGURED	\N	2026-08-19 18:07:26.79446
2626	openai	NOT_CONFIGURED	\N	2026-08-19 18:07:26.79446
2627	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:07:26.79446
2628	simulation	HEALTHY	\N	2026-08-19 18:07:26.79446
2629	application	HEALTHY	4.5	2026-08-19 18:07:26.79446
2630	database	HEALTHY	1.01	2026-08-19 18:07:56.8419
2631	redis	NOT_CONFIGURED	\N	2026-08-19 18:07:56.8419
2632	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:07:56.8419
2633	celery	NOT_CONFIGURED	\N	2026-08-19 18:07:56.8419
2634	email	HEALTHY	\N	2026-08-19 18:07:56.8419
2635	backup	UNAVAILABLE	\N	2026-08-19 18:07:56.8419
2636	sentry	NOT_CONFIGURED	\N	2026-08-19 18:07:56.8419
2637	openai	NOT_CONFIGURED	\N	2026-08-19 18:07:56.8419
2638	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:07:56.842919
2639	simulation	HEALTHY	\N	2026-08-19 18:07:56.842919
2640	application	HEALTHY	4.5	2026-08-19 18:07:56.842919
2641	database	HEALTHY	0.77	2026-08-19 18:08:26.885614
2642	redis	NOT_CONFIGURED	\N	2026-08-19 18:08:26.885614
2643	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:08:26.886594
2644	celery	NOT_CONFIGURED	\N	2026-08-19 18:08:26.886594
2645	email	HEALTHY	\N	2026-08-19 18:08:26.886594
2646	backup	UNAVAILABLE	\N	2026-08-19 18:08:26.886594
2647	sentry	NOT_CONFIGURED	\N	2026-08-19 18:08:26.886594
2648	openai	NOT_CONFIGURED	\N	2026-08-19 18:08:26.886594
2649	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:08:26.886594
2650	simulation	HEALTHY	\N	2026-08-19 18:08:26.886594
2651	application	HEALTHY	4.5	2026-08-19 18:08:26.886594
2652	database	HEALTHY	1	2026-08-19 18:08:56.920829
2653	redis	NOT_CONFIGURED	\N	2026-08-19 18:08:56.92183
2654	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:08:56.92183
2655	celery	NOT_CONFIGURED	\N	2026-08-19 18:08:56.92183
2656	email	HEALTHY	\N	2026-08-19 18:08:56.92183
2657	backup	UNAVAILABLE	\N	2026-08-19 18:08:56.92183
2658	sentry	NOT_CONFIGURED	\N	2026-08-19 18:08:56.92183
2659	openai	NOT_CONFIGURED	\N	2026-08-19 18:08:56.92183
2660	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:08:56.92183
2661	simulation	HEALTHY	\N	2026-08-19 18:08:56.92183
2662	application	HEALTHY	4.5	2026-08-19 18:08:56.92183
2663	database	HEALTHY	0	2026-08-19 18:09:26.951583
2664	redis	NOT_CONFIGURED	\N	2026-08-19 18:09:26.951583
2665	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:09:26.951583
2666	celery	NOT_CONFIGURED	\N	2026-08-19 18:09:26.951583
2667	email	HEALTHY	\N	2026-08-19 18:09:26.951583
2668	backup	UNAVAILABLE	\N	2026-08-19 18:09:26.951583
2669	sentry	NOT_CONFIGURED	\N	2026-08-19 18:09:26.951583
2670	openai	NOT_CONFIGURED	\N	2026-08-19 18:09:26.951583
2671	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:09:26.951583
2672	simulation	HEALTHY	\N	2026-08-19 18:09:26.951583
2673	application	HEALTHY	4.5	2026-08-19 18:09:26.951583
2674	database	HEALTHY	1	2026-08-19 18:09:56.980211
2675	redis	NOT_CONFIGURED	\N	2026-08-19 18:09:56.980211
2676	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:09:56.980211
2677	celery	NOT_CONFIGURED	\N	2026-08-19 18:09:56.980211
2678	email	HEALTHY	\N	2026-08-19 18:09:56.980211
2679	backup	UNAVAILABLE	\N	2026-08-19 18:09:56.980211
2680	sentry	NOT_CONFIGURED	\N	2026-08-19 18:09:56.980211
2681	openai	NOT_CONFIGURED	\N	2026-08-19 18:09:56.980211
2682	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:09:56.980211
2683	simulation	HEALTHY	\N	2026-08-19 18:09:56.980211
2684	application	HEALTHY	4.5	2026-08-19 18:09:56.980211
2685	database	HEALTHY	0	2026-08-19 18:10:27.031496
2686	redis	NOT_CONFIGURED	\N	2026-08-19 18:10:27.031496
2687	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:10:27.031496
2688	celery	NOT_CONFIGURED	\N	2026-08-19 18:10:27.032495
2689	email	HEALTHY	\N	2026-08-19 18:10:27.032495
2690	backup	UNAVAILABLE	\N	2026-08-19 18:10:27.032495
2691	sentry	NOT_CONFIGURED	\N	2026-08-19 18:10:27.032495
2692	openai	NOT_CONFIGURED	\N	2026-08-19 18:10:27.032495
2693	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:10:27.032495
2694	simulation	HEALTHY	\N	2026-08-19 18:10:27.032495
2695	application	HEALTHY	4.5	2026-08-19 18:10:27.032495
2696	database	HEALTHY	1.01	2026-08-19 18:10:57.109094
2697	redis	NOT_CONFIGURED	\N	2026-08-19 18:10:57.109094
2698	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:10:57.109094
2699	celery	NOT_CONFIGURED	\N	2026-08-19 18:10:57.109094
2700	email	HEALTHY	\N	2026-08-19 18:10:57.109094
2701	backup	UNAVAILABLE	\N	2026-08-19 18:10:57.109094
2702	sentry	NOT_CONFIGURED	\N	2026-08-19 18:10:57.109094
2703	openai	NOT_CONFIGURED	\N	2026-08-19 18:10:57.109094
2704	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:10:57.109094
2705	simulation	HEALTHY	\N	2026-08-19 18:10:57.109094
2706	application	HEALTHY	4.5	2026-08-19 18:10:57.109094
2707	database	HEALTHY	0	2026-08-19 18:11:27.163317
2708	redis	NOT_CONFIGURED	\N	2026-08-19 18:11:27.163317
2709	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:11:27.163317
2710	celery	NOT_CONFIGURED	\N	2026-08-19 18:11:27.163317
2711	email	HEALTHY	\N	2026-08-19 18:11:27.163317
2712	backup	UNAVAILABLE	\N	2026-08-19 18:11:27.163317
2713	sentry	NOT_CONFIGURED	\N	2026-08-19 18:11:27.163317
2714	openai	NOT_CONFIGURED	\N	2026-08-19 18:11:27.163317
2715	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:11:27.163317
2716	simulation	HEALTHY	\N	2026-08-19 18:11:27.163317
2717	application	HEALTHY	4.5	2026-08-19 18:11:27.163317
2718	database	HEALTHY	1	2026-08-19 18:11:57.189044
2719	redis	NOT_CONFIGURED	\N	2026-08-19 18:11:57.189044
2720	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:11:57.189044
2721	celery	NOT_CONFIGURED	\N	2026-08-19 18:11:57.189044
2722	email	HEALTHY	\N	2026-08-19 18:11:57.189044
2723	backup	UNAVAILABLE	\N	2026-08-19 18:11:57.189044
2724	sentry	NOT_CONFIGURED	\N	2026-08-19 18:11:57.189044
2725	openai	NOT_CONFIGURED	\N	2026-08-19 18:11:57.189044
2726	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:11:57.189044
2727	simulation	HEALTHY	\N	2026-08-19 18:11:57.189044
2728	application	HEALTHY	4.5	2026-08-19 18:11:57.189044
2729	database	HEALTHY	11.29	2026-08-19 18:12:27.294227
2730	redis	NOT_CONFIGURED	\N	2026-08-19 18:12:27.295229
2731	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:12:27.295229
2732	celery	NOT_CONFIGURED	\N	2026-08-19 18:12:27.295229
2733	email	HEALTHY	\N	2026-08-19 18:12:27.295229
2734	backup	UNAVAILABLE	\N	2026-08-19 18:12:27.295229
2735	sentry	NOT_CONFIGURED	\N	2026-08-19 18:12:27.295229
2736	openai	NOT_CONFIGURED	\N	2026-08-19 18:12:27.295229
2737	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:12:27.295229
2738	simulation	HEALTHY	\N	2026-08-19 18:12:27.295229
2739	application	HEALTHY	4.5	2026-08-19 18:12:27.295229
2740	database	HEALTHY	0.99	2026-08-19 18:12:57.319008
2741	redis	NOT_CONFIGURED	\N	2026-08-19 18:12:57.319008
2742	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:12:57.319008
2743	celery	NOT_CONFIGURED	\N	2026-08-19 18:12:57.320004
2744	email	HEALTHY	\N	2026-08-19 18:12:57.320004
2745	backup	UNAVAILABLE	\N	2026-08-19 18:12:57.320004
2746	sentry	NOT_CONFIGURED	\N	2026-08-19 18:12:57.320004
2747	openai	NOT_CONFIGURED	\N	2026-08-19 18:12:57.320004
2748	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:12:57.320004
2749	simulation	HEALTHY	\N	2026-08-19 18:12:57.320004
2750	application	HEALTHY	4.5	2026-08-19 18:12:57.320004
2751	database	HEALTHY	1.13	2026-08-19 18:13:27.34698
2752	redis	NOT_CONFIGURED	\N	2026-08-19 18:13:27.348433
2753	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:13:27.348433
2754	celery	NOT_CONFIGURED	\N	2026-08-19 18:13:27.348433
2755	email	HEALTHY	\N	2026-08-19 18:13:27.348433
2756	backup	UNAVAILABLE	\N	2026-08-19 18:13:27.348433
2757	sentry	NOT_CONFIGURED	\N	2026-08-19 18:13:27.348433
2758	openai	NOT_CONFIGURED	\N	2026-08-19 18:13:27.348433
2759	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:13:27.348433
2760	simulation	HEALTHY	\N	2026-08-19 18:13:27.348433
2761	application	HEALTHY	4.5	2026-08-19 18:13:27.348433
2762	database	HEALTHY	3.51	2026-08-19 18:13:57.443364
2763	redis	NOT_CONFIGURED	\N	2026-08-19 18:13:57.443364
2764	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:13:57.443364
2765	celery	NOT_CONFIGURED	\N	2026-08-19 18:13:57.443364
2766	email	HEALTHY	\N	2026-08-19 18:13:57.443364
2767	backup	UNAVAILABLE	\N	2026-08-19 18:13:57.443364
2768	sentry	NOT_CONFIGURED	\N	2026-08-19 18:13:57.443364
2769	openai	NOT_CONFIGURED	\N	2026-08-19 18:13:57.443364
2770	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:13:57.443364
2771	simulation	HEALTHY	\N	2026-08-19 18:13:57.443364
2772	application	HEALTHY	4.5	2026-08-19 18:13:57.443364
2773	database	HEALTHY	1	2026-08-19 18:14:44.167485
2774	redis	NOT_CONFIGURED	\N	2026-08-19 18:14:44.167485
2775	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:14:44.167485
2776	celery	NOT_CONFIGURED	\N	2026-08-19 18:14:44.167485
2777	email	HEALTHY	\N	2026-08-19 18:14:44.167485
2778	backup	HEALTHY	\N	2026-08-19 18:14:44.167485
2779	sentry	NOT_CONFIGURED	\N	2026-08-19 18:14:44.167485
2780	openai	NOT_CONFIGURED	\N	2026-08-19 18:14:44.167485
2781	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:14:44.167485
2782	simulation	HEALTHY	\N	2026-08-19 18:14:44.167485
2783	application	HEALTHY	4.5	2026-08-19 18:14:44.167485
2784	database	HEALTHY	0.54	2026-08-19 18:15:14.21573
2785	redis	NOT_CONFIGURED	\N	2026-08-19 18:15:14.21573
2786	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:15:14.21573
2787	celery	NOT_CONFIGURED	\N	2026-08-19 18:15:14.21573
2788	email	HEALTHY	\N	2026-08-19 18:15:14.21573
2789	backup	UNAVAILABLE	\N	2026-08-19 18:15:14.21573
2790	sentry	NOT_CONFIGURED	\N	2026-08-19 18:15:14.21573
2791	openai	NOT_CONFIGURED	\N	2026-08-19 18:15:14.21573
2792	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:15:14.21573
2793	simulation	HEALTHY	\N	2026-08-19 18:15:14.21573
2794	application	HEALTHY	4.5	2026-08-19 18:15:14.21573
3059	database	HEALTHY	0	2026-08-19 18:23:44.9221
3060	redis	NOT_CONFIGURED	\N	2026-08-19 18:23:44.9221
3061	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:23:44.9221
3062	celery	NOT_CONFIGURED	\N	2026-08-19 18:23:44.9221
3063	email	HEALTHY	\N	2026-08-19 18:23:44.9221
3064	backup	UNAVAILABLE	\N	2026-08-19 18:23:44.9221
3065	sentry	NOT_CONFIGURED	\N	2026-08-19 18:23:44.9221
3066	openai	NOT_CONFIGURED	\N	2026-08-19 18:23:44.9221
3067	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:23:44.9221
3068	simulation	HEALTHY	\N	2026-08-19 18:23:44.9221
3069	application	HEALTHY	4.5	2026-08-19 18:23:44.9221
\.


--
-- Data for Name: system_incidents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_incidents (id, category, severity, title, description, source, status, fingerprint, started_at, resolved_at, acknowledged_by, created_at) FROM stdin;
6	DATABASE	CRITICAL	Postgres Connection Fail	Database disconnected during test	test	RESOLVED	TEST_DB_OFFLINE	2026-08-19 18:22:51.311948	2026-08-19 18:22:51.373068	test_manager	2026-08-19 18:22:51.313948
\.


--
-- Data for Name: task_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task_events (id, task_id, event_type, previous_status, new_status, user_id, created_at, reason, metadata) FROM stdin;
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (id, task_number, warehouse_id, task_type, priority, priority_score, status, source_type, source_id, order_id, order_item_id, product_id, source_location_id, destination_location_id, requested_quantity, completed_quantity, assigned_user_id, assigned_robot_id, created_at, prioritized_at, assigned_at, started_at, paused_at, completed_at, failed_at, cancelled_at, due_at, retry_count, failure_reason, notes, metadata, depends_on_task_id) FROM stdin;
\.


--
-- Data for Name: user_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_sessions (id, user_id, session_token_hash, created_at, last_seen_at, expires_at, revoked_at, revoke_reason, login_method, ip_address, login_location, user_agent) FROM stdin;
\.


--
-- Data for Name: user_warehouse_access; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_warehouse_access (id, user_id, warehouse_id, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, password_hash, role, full_name, google_subject_id, created_at, updated_at, is_active, is_verified, last_login_at, last_logout_at, last_login_ip, login_location, login_method, failed_login_count, locked_until, email_verified_at, password_changed_at) FROM stdin;
4	test_viewer	\N	$2b$12$nQPG2Um5UqZfI6jK3B6.WetOxegfqLhd6Pce1RI9tUCKHBMph6XAy	viewer		\N	2026-08-19 15:43:35.82341	2026-08-19 18:19:39.737522	t	t	2026-08-19 18:19:39.736398	\N	testclient	\N	password	0	\N	\N	\N
3	test_manager	\N	$2b$12$GFo8sE.n54/fIADXyKInkucviTcgbabSwv8GzwGEvt397RMAB5bmO	manager		\N	2026-08-19 15:43:35.82341	2026-08-19 18:20:02.256244	t	t	2026-08-19 18:20:02.253668	\N	testclient	\N	password	0	\N	\N	\N
1	admin	\N	$2b$12$ZBDm0khkDRbz0JCeYWHKweMqEuIQNPH4U39P4IhVqCAKD5RILGQrK	admin	System Administrator	\N	2026-08-19 15:43:01.098298	2026-08-19 18:18:36.662353	t	t	2026-08-19 18:18:36.656975	\N	testclient	\N	password	0	\N	\N	\N
2	test_admin	\N	$2b$12$6r11Vxdfp6ZAFSeRFIDIqezssLxtfn8KMuApYPmwW6UwYWNlrOZYO	admin		\N	2026-08-19 15:43:35.82341	2026-08-19 18:24:13.368019	t	t	2026-08-19 18:20:36.505089	\N	testclient	\N	recovery	1	\N	\N	2026-08-19 18:20:15.721325
5	test_admin_hardened	\N	$2b$12$84cr.UVx0AzxuMsHIMGm7.rRHF2IndskJ7.2ytRfZF/BWKznDLGvq	admin		\N	2026-08-19 15:43:35.82341	2026-08-19 18:24:17.910298	t	t	2026-08-19 18:24:17.906274	\N	testclient	\N	password	0	\N	\N	\N
\.


--
-- Data for Name: warehouse_grid_cells; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.warehouse_grid_cells (id, warehouse_id, x, y, cell_type, traversable, occupied, restricted, cost, metadata) FROM stdin;
\.


--
-- Data for Name: warehouse_locations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.warehouse_locations (id, warehouse_id, zone, aisle, rack, shelf, x, y, capacity, current_utilization, location_type, status, created_at) FROM stdin;
\.


--
-- Data for Name: warehouse_obstacles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.warehouse_obstacles (id, warehouse_id, obstacle_type, x, y, width, height, active, severity, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: warehouses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.warehouses (id, name, location, latitude, longitude, created_at) FROM stdin;
WH-BLR-01	Bangalore Fulfillment Center	Bangalore, Karnataka	12.971598	77.594566	2026-08-19 18:23:32.770576
WH-CHN-01	Chennai Port Logistics Hub	Chennai, Tamil Nadu	13.08268	80.270718	2026-08-19 18:23:32.790757
WH-BOM-01	Mumbai Container Terminal	Mumbai, Maharashtra	19.07609	72.877701	2026-08-19 18:23:32.794829
WH-DEL-01	Delhi NCR Logistics Park	Noida, Uttar Pradesh	28.535517	77.391029	2026-08-19 18:23:32.801022
WH-CCU-01	Kolkata Gateway Depot	Kolkata, West Bengal	22.572646	88.363895	2026-08-19 18:23:32.805656
\.


--
-- Name: access_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.access_log_id_seq', 533, true);


--
-- Name: ai_recommendations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ai_recommendations_id_seq', 151, true);


--
-- Name: audit_ledger_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_ledger_id_seq', 729, true);


--
-- Name: backup_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.backup_records_id_seq', 13, true);


--
-- Name: digital_twin_simulations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.digital_twin_simulations_id_seq', 4, true);


--
-- Name: experiment_runs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.experiment_runs_id_seq', 1, false);


--
-- Name: experiments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.experiments_id_seq', 2, true);


--
-- Name: health_thresholds_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.health_thresholds_id_seq', 23, true);


--
-- Name: inventory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventory_id_seq', 344, true);


--
-- Name: inventory_reservations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventory_reservations_id_seq', 4, true);


--
-- Name: notification_preferences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notification_preferences_id_seq', 1, true);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notifications_id_seq', 202, true);


--
-- Name: order_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.order_events_id_seq', 1, true);


--
-- Name: order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.order_items_id_seq', 4, true);


--
-- Name: otp_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.otp_records_id_seq', 4, true);


--
-- Name: packing_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.packing_records_id_seq', 1, false);


--
-- Name: recovery_codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.recovery_codes_id_seq', 8, true);


--
-- Name: recovery_credentials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.recovery_credentials_id_seq', 1, true);


--
-- Name: robot_reservations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.robot_reservations_id_seq', 55, true);


--
-- Name: robot_routes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.robot_routes_id_seq', 18, true);


--
-- Name: robot_telemetry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.robot_telemetry_id_seq', 49, true);


--
-- Name: robots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.robots_id_seq', 84, true);


--
-- Name: scenarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.scenarios_id_seq', 2, true);


--
-- Name: shrinkage_flags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.shrinkage_flags_id_seq', 18, true);


--
-- Name: simulation_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.simulation_events_id_seq', 8, true);


--
-- Name: simulation_snapshots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.simulation_snapshots_id_seq', 5, true);


--
-- Name: stock_movements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.stock_movements_id_seq', 9665, true);


--
-- Name: system_health_snapshots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_health_snapshots_id_seq', 3091, true);


--
-- Name: system_incidents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_incidents_id_seq', 6, true);


--
-- Name: task_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.task_events_id_seq', 26, true);


--
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tasks_id_seq', 23, true);


--
-- Name: user_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_sessions_id_seq', 1, false);


--
-- Name: user_warehouse_access_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_warehouse_access_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 20, true);


--
-- Name: warehouse_grid_cells_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.warehouse_grid_cells_id_seq', 780, true);


--
-- Name: warehouse_obstacles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.warehouse_obstacles_id_seq', 2, true);


--
-- Name: access_log access_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.access_log
    ADD CONSTRAINT access_log_pkey PRIMARY KEY (id);


--
-- Name: ai_recommendations ai_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_recommendations
    ADD CONSTRAINT ai_recommendations_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_ledger audit_ledger_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_ledger
    ADD CONSTRAINT audit_ledger_pkey PRIMARY KEY (id);


--
-- Name: backup_records backup_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backup_records
    ADD CONSTRAINT backup_records_pkey PRIMARY KEY (id);


--
-- Name: digital_twin_simulations digital_twin_simulations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.digital_twin_simulations
    ADD CONSTRAINT digital_twin_simulations_pkey PRIMARY KEY (id);


--
-- Name: experiment_runs experiment_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_runs
    ADD CONSTRAINT experiment_runs_pkey PRIMARY KEY (id);


--
-- Name: experiments experiments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiments
    ADD CONSTRAINT experiments_pkey PRIMARY KEY (id);


--
-- Name: health_thresholds health_thresholds_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.health_thresholds
    ADD CONSTRAINT health_thresholds_pkey PRIMARY KEY (id);


--
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (id);


--
-- Name: inventory_reservations inventory_reservations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_reservations
    ADD CONSTRAINT inventory_reservations_pkey PRIMARY KEY (id);


--
-- Name: items items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (id);


--
-- Name: notification_preferences notification_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_preferences
    ADD CONSTRAINT notification_preferences_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_idempotency_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_idempotency_key_key UNIQUE (idempotency_key);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: order_events order_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_events
    ADD CONSTRAINT order_events_pkey PRIMARY KEY (id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: otp_records otp_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otp_records
    ADD CONSTRAINT otp_records_pkey PRIMARY KEY (id);


--
-- Name: packing_records packing_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.packing_records
    ADD CONSTRAINT packing_records_pkey PRIMARY KEY (id);


--
-- Name: recovery_codes recovery_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recovery_codes
    ADD CONSTRAINT recovery_codes_pkey PRIMARY KEY (id);


--
-- Name: recovery_credentials recovery_credentials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recovery_credentials
    ADD CONSTRAINT recovery_credentials_pkey PRIMARY KEY (id);


--
-- Name: robot_reservations robot_reservations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_reservations
    ADD CONSTRAINT robot_reservations_pkey PRIMARY KEY (id);


--
-- Name: robot_routes robot_routes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_routes
    ADD CONSTRAINT robot_routes_pkey PRIMARY KEY (id);


--
-- Name: robot_telemetry robot_telemetry_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_telemetry
    ADD CONSTRAINT robot_telemetry_pkey PRIMARY KEY (id);


--
-- Name: robots robots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robots
    ADD CONSTRAINT robots_pkey PRIMARY KEY (id);


--
-- Name: scenarios scenarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scenarios
    ADD CONSTRAINT scenarios_pkey PRIMARY KEY (id);


--
-- Name: shipments shipments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipments_pkey PRIMARY KEY (id);


--
-- Name: shrinkage_flags shrinkage_flags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shrinkage_flags
    ADD CONSTRAINT shrinkage_flags_pkey PRIMARY KEY (id);


--
-- Name: simulation_events simulation_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_events
    ADD CONSTRAINT simulation_events_pkey PRIMARY KEY (id);


--
-- Name: simulation_snapshots simulation_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_snapshots
    ADD CONSTRAINT simulation_snapshots_pkey PRIMARY KEY (id);


--
-- Name: stock_movements stock_movements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_pkey PRIMARY KEY (id);


--
-- Name: system_health_snapshots system_health_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_health_snapshots
    ADD CONSTRAINT system_health_snapshots_pkey PRIMARY KEY (id);


--
-- Name: system_incidents system_incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_incidents
    ADD CONSTRAINT system_incidents_pkey PRIMARY KEY (id);


--
-- Name: task_events task_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_events
    ADD CONSTRAINT task_events_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: warehouse_grid_cells uq_grid_cell; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_grid_cells
    ADD CONSTRAINT uq_grid_cell UNIQUE (warehouse_id, x, y);


--
-- Name: stock_movements uq_movement; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT uq_movement UNIQUE (date, warehouse_id, item_id);


--
-- Name: otp_records uq_otp_user_purpose; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otp_records
    ADD CONSTRAINT uq_otp_user_purpose UNIQUE (user_id, purpose);


--
-- Name: notification_preferences uq_user_category_preference; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_preferences
    ADD CONSTRAINT uq_user_category_preference UNIQUE (user_id, category);


--
-- Name: user_warehouse_access uq_user_warehouse; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_warehouse_access
    ADD CONSTRAINT uq_user_warehouse UNIQUE (user_id, warehouse_id);


--
-- Name: inventory uq_warehouse_item_location; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT uq_warehouse_item_location UNIQUE (warehouse_id, item_id, location_id);


--
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (id);


--
-- Name: user_sessions user_sessions_session_token_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_session_token_hash_key UNIQUE (session_token_hash);


--
-- Name: user_warehouse_access user_warehouse_access_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_warehouse_access
    ADD CONSTRAINT user_warehouse_access_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: warehouse_grid_cells warehouse_grid_cells_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_grid_cells
    ADD CONSTRAINT warehouse_grid_cells_pkey PRIMARY KEY (id);


--
-- Name: warehouse_locations warehouse_locations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_locations
    ADD CONSTRAINT warehouse_locations_pkey PRIMARY KEY (id);


--
-- Name: warehouse_obstacles warehouse_obstacles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_obstacles
    ADD CONSTRAINT warehouse_obstacles_pkey PRIMARY KEY (id);


--
-- Name: warehouses warehouses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_pkey PRIMARY KEY (id);


--
-- Name: ix_access_log_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_access_log_timestamp ON public.access_log USING btree ("timestamp");


--
-- Name: ix_ai_recommendations_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ai_recommendations_created_at ON public.ai_recommendations USING btree (created_at);


--
-- Name: ix_ai_recommendations_recommendation_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ai_recommendations_recommendation_type ON public.ai_recommendations USING btree (recommendation_type);


--
-- Name: ix_ai_recommendations_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ai_recommendations_timestamp ON public.ai_recommendations USING btree ("timestamp");


--
-- Name: ix_backup_records_backup_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_backup_records_backup_id ON public.backup_records USING btree (backup_id);


--
-- Name: ix_backup_records_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_backup_records_created_at ON public.backup_records USING btree (created_at);


--
-- Name: ix_digital_twin_simulations_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_digital_twin_simulations_created_at ON public.digital_twin_simulations USING btree (created_at);


--
-- Name: ix_digital_twin_simulations_simulation_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_digital_twin_simulations_simulation_status ON public.digital_twin_simulations USING btree (simulation_status);


--
-- Name: ix_digital_twin_simulations_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_digital_twin_simulations_warehouse_id ON public.digital_twin_simulations USING btree (warehouse_id);


--
-- Name: ix_experiment_runs_experiment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_experiment_runs_experiment_id ON public.experiment_runs USING btree (experiment_id);


--
-- Name: ix_experiments_scenario_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_experiments_scenario_id ON public.experiments USING btree (scenario_id);


--
-- Name: ix_health_thresholds_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_health_thresholds_key ON public.health_thresholds USING btree (key);


--
-- Name: ix_inventory_item_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inventory_item_id ON public.inventory USING btree (item_id);


--
-- Name: ix_inventory_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inventory_location_id ON public.inventory USING btree (location_id);


--
-- Name: ix_inventory_reservations_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inventory_reservations_created_at ON public.inventory_reservations USING btree (created_at);


--
-- Name: ix_inventory_reservations_item_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inventory_reservations_item_id ON public.inventory_reservations USING btree (item_id);


--
-- Name: ix_inventory_reservations_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inventory_reservations_location_id ON public.inventory_reservations USING btree (location_id);


--
-- Name: ix_inventory_reservations_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inventory_reservations_order_id ON public.inventory_reservations USING btree (order_id);


--
-- Name: ix_inventory_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inventory_warehouse_id ON public.inventory USING btree (warehouse_id);


--
-- Name: ix_items_sku; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_items_sku ON public.items USING btree (sku);


--
-- Name: ix_notification_preferences_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_preferences_category ON public.notification_preferences USING btree (category);


--
-- Name: ix_notification_preferences_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_preferences_user_id ON public.notification_preferences USING btree (user_id);


--
-- Name: ix_notifications_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_created_at ON public.notifications USING btree (created_at);


--
-- Name: ix_notifications_event_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_event_type ON public.notifications USING btree (event_type);


--
-- Name: ix_notifications_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_status ON public.notifications USING btree (status);


--
-- Name: ix_notifications_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_user_id ON public.notifications USING btree (user_id);


--
-- Name: ix_notifications_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_warehouse_id ON public.notifications USING btree (warehouse_id);


--
-- Name: ix_order_events_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_order_events_order_id ON public.order_events USING btree (order_id);


--
-- Name: ix_order_events_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_order_events_timestamp ON public.order_events USING btree ("timestamp");


--
-- Name: ix_order_items_item_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_order_items_item_id ON public.order_items USING btree (item_id);


--
-- Name: ix_order_items_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_order_items_order_id ON public.order_items USING btree (order_id);


--
-- Name: ix_orders_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_created_at ON public.orders USING btree (created_at);


--
-- Name: ix_orders_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_status ON public.orders USING btree (status);


--
-- Name: ix_orders_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_warehouse_id ON public.orders USING btree (warehouse_id);


--
-- Name: ix_otp_records_expires_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_otp_records_expires_at ON public.otp_records USING btree (expires_at);


--
-- Name: ix_otp_records_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_otp_records_user_id ON public.otp_records USING btree (user_id);


--
-- Name: ix_packing_records_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_packing_records_order_id ON public.packing_records USING btree (order_id);


--
-- Name: ix_recovery_codes_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recovery_codes_user_id ON public.recovery_codes USING btree (user_id);


--
-- Name: ix_recovery_credentials_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_recovery_credentials_user_id ON public.recovery_credentials USING btree (user_id);


--
-- Name: ix_robot_reservations_robot_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robot_reservations_robot_id ON public.robot_reservations USING btree (robot_id);


--
-- Name: ix_robot_reservations_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robot_reservations_warehouse_id ON public.robot_reservations USING btree (warehouse_id);


--
-- Name: ix_robot_routes_robot_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robot_routes_robot_id ON public.robot_routes USING btree (robot_id);


--
-- Name: ix_robot_routes_task_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robot_routes_task_id ON public.robot_routes USING btree (task_id);


--
-- Name: ix_robot_routes_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robot_routes_warehouse_id ON public.robot_routes USING btree (warehouse_id);


--
-- Name: ix_robot_telemetry_robot_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robot_telemetry_robot_id ON public.robot_telemetry USING btree (robot_id);


--
-- Name: ix_robot_telemetry_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robot_telemetry_timestamp ON public.robot_telemetry USING btree ("timestamp");


--
-- Name: ix_robots_assigned_task_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robots_assigned_task_id ON public.robots USING btree (assigned_task_id);


--
-- Name: ix_robots_current_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robots_current_location_id ON public.robots USING btree (current_location_id);


--
-- Name: ix_robots_robot_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_robots_robot_code ON public.robots USING btree (robot_code);


--
-- Name: ix_robots_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robots_status ON public.robots USING btree (status);


--
-- Name: ix_robots_target_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robots_target_location_id ON public.robots USING btree (target_location_id);


--
-- Name: ix_robots_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robots_warehouse_id ON public.robots USING btree (warehouse_id);


--
-- Name: ix_scenarios_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scenarios_warehouse_id ON public.scenarios USING btree (warehouse_id);


--
-- Name: ix_shipments_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipments_order_id ON public.shipments USING btree (order_id);


--
-- Name: ix_simulation_events_event_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_events_event_type ON public.simulation_events USING btree (event_type);


--
-- Name: ix_simulation_events_real_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_events_real_timestamp ON public.simulation_events USING btree (real_timestamp);


--
-- Name: ix_simulation_events_robot_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_events_robot_id ON public.simulation_events USING btree (robot_id);


--
-- Name: ix_simulation_events_simulation_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_events_simulation_id ON public.simulation_events USING btree (simulation_id);


--
-- Name: ix_simulation_events_task_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_events_task_id ON public.simulation_events USING btree (task_id);


--
-- Name: ix_simulation_events_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_events_warehouse_id ON public.simulation_events USING btree (warehouse_id);


--
-- Name: ix_simulation_snapshots_simulation_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_snapshots_simulation_id ON public.simulation_snapshots USING btree (simulation_id);


--
-- Name: ix_simulation_snapshots_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_snapshots_warehouse_id ON public.simulation_snapshots USING btree (warehouse_id);


--
-- Name: ix_stock_movements_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_date ON public.stock_movements USING btree (date);


--
-- Name: ix_stock_movements_item_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_item_id ON public.stock_movements USING btree (item_id);


--
-- Name: ix_stock_movements_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_warehouse_id ON public.stock_movements USING btree (warehouse_id);


--
-- Name: ix_system_health_snapshots_service; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_system_health_snapshots_service ON public.system_health_snapshots USING btree (service);


--
-- Name: ix_system_health_snapshots_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_system_health_snapshots_timestamp ON public.system_health_snapshots USING btree ("timestamp");


--
-- Name: ix_system_incidents_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_system_incidents_category ON public.system_incidents USING btree (category);


--
-- Name: ix_system_incidents_fingerprint; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_system_incidents_fingerprint ON public.system_incidents USING btree (fingerprint);


--
-- Name: ix_task_events_task_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_task_events_task_id ON public.task_events USING btree (task_id);


--
-- Name: ix_tasks_assigned_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_assigned_user_id ON public.tasks USING btree (assigned_user_id);


--
-- Name: ix_tasks_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_created_at ON public.tasks USING btree (created_at);


--
-- Name: ix_tasks_destination_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_destination_location_id ON public.tasks USING btree (destination_location_id);


--
-- Name: ix_tasks_due_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_due_at ON public.tasks USING btree (due_at);


--
-- Name: ix_tasks_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_order_id ON public.tasks USING btree (order_id);


--
-- Name: ix_tasks_order_item_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_order_item_id ON public.tasks USING btree (order_item_id);


--
-- Name: ix_tasks_priority_score; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_priority_score ON public.tasks USING btree (priority_score);


--
-- Name: ix_tasks_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_product_id ON public.tasks USING btree (product_id);


--
-- Name: ix_tasks_source_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_source_location_id ON public.tasks USING btree (source_location_id);


--
-- Name: ix_tasks_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_status ON public.tasks USING btree (status);


--
-- Name: ix_tasks_task_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_tasks_task_number ON public.tasks USING btree (task_number);


--
-- Name: ix_tasks_task_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_task_type ON public.tasks USING btree (task_type);


--
-- Name: ix_tasks_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_warehouse_id ON public.tasks USING btree (warehouse_id);


--
-- Name: ix_user_sessions_expires_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_sessions_expires_at ON public.user_sessions USING btree (expires_at);


--
-- Name: ix_user_sessions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_sessions_user_id ON public.user_sessions USING btree (user_id);


--
-- Name: ix_user_warehouse_access_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_warehouse_access_user_id ON public.user_warehouse_access USING btree (user_id);


--
-- Name: ix_user_warehouse_access_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_warehouse_access_warehouse_id ON public.user_warehouse_access USING btree (warehouse_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_google_subject_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_google_subject_id ON public.users USING btree (google_subject_id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_warehouse_grid_cells_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_grid_cells_warehouse_id ON public.warehouse_grid_cells USING btree (warehouse_id);


--
-- Name: ix_warehouse_locations_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_locations_warehouse_id ON public.warehouse_locations USING btree (warehouse_id);


--
-- Name: ix_warehouse_obstacles_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_obstacles_warehouse_id ON public.warehouse_obstacles USING btree (warehouse_id);


--
-- Name: digital_twin_simulations digital_twin_simulations_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.digital_twin_simulations
    ADD CONSTRAINT digital_twin_simulations_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: experiment_runs experiment_runs_experiment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_runs
    ADD CONSTRAINT experiment_runs_experiment_id_fkey FOREIGN KEY (experiment_id) REFERENCES public.experiments(id) ON DELETE CASCADE;


--
-- Name: experiments experiments_scenario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiments
    ADD CONSTRAINT experiments_scenario_id_fkey FOREIGN KEY (scenario_id) REFERENCES public.scenarios(id) ON DELETE CASCADE;


--
-- Name: inventory inventory_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id) ON DELETE CASCADE;


--
-- Name: inventory inventory_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.warehouse_locations(id) ON DELETE SET NULL;


--
-- Name: inventory_reservations inventory_reservations_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_reservations
    ADD CONSTRAINT inventory_reservations_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id) ON DELETE CASCADE;


--
-- Name: inventory_reservations inventory_reservations_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_reservations
    ADD CONSTRAINT inventory_reservations_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.warehouse_locations(id) ON DELETE SET NULL;


--
-- Name: inventory_reservations inventory_reservations_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_reservations
    ADD CONSTRAINT inventory_reservations_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: inventory inventory_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: notification_preferences notification_preferences_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_preferences
    ADD CONSTRAINT notification_preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: notifications notifications_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: order_events order_events_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_events
    ADD CONSTRAINT order_events_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: order_items order_items_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id) ON DELETE CASCADE;


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: orders orders_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: otp_records otp_records_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otp_records
    ADD CONSTRAINT otp_records_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: packing_records packing_records_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.packing_records
    ADD CONSTRAINT packing_records_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: recovery_codes recovery_codes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recovery_codes
    ADD CONSTRAINT recovery_codes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: recovery_credentials recovery_credentials_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recovery_credentials
    ADD CONSTRAINT recovery_credentials_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: robot_reservations robot_reservations_robot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_reservations
    ADD CONSTRAINT robot_reservations_robot_id_fkey FOREIGN KEY (robot_id) REFERENCES public.robots(id) ON DELETE CASCADE;


--
-- Name: robot_reservations robot_reservations_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_reservations
    ADD CONSTRAINT robot_reservations_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: robot_routes robot_routes_robot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_routes
    ADD CONSTRAINT robot_routes_robot_id_fkey FOREIGN KEY (robot_id) REFERENCES public.robots(id) ON DELETE CASCADE;


--
-- Name: robot_routes robot_routes_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_routes
    ADD CONSTRAINT robot_routes_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id) ON DELETE SET NULL;


--
-- Name: robot_routes robot_routes_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_routes
    ADD CONSTRAINT robot_routes_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: robot_telemetry robot_telemetry_robot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_telemetry
    ADD CONSTRAINT robot_telemetry_robot_id_fkey FOREIGN KEY (robot_id) REFERENCES public.robots(id) ON DELETE CASCADE;


--
-- Name: robots robots_assigned_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robots
    ADD CONSTRAINT robots_assigned_task_id_fkey FOREIGN KEY (assigned_task_id) REFERENCES public.tasks(id) ON DELETE SET NULL;


--
-- Name: robots robots_current_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robots
    ADD CONSTRAINT robots_current_location_id_fkey FOREIGN KEY (current_location_id) REFERENCES public.warehouse_locations(id) ON DELETE SET NULL;


--
-- Name: robots robots_target_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robots
    ADD CONSTRAINT robots_target_location_id_fkey FOREIGN KEY (target_location_id) REFERENCES public.warehouse_locations(id) ON DELETE SET NULL;


--
-- Name: robots robots_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robots
    ADD CONSTRAINT robots_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: scenarios scenarios_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scenarios
    ADD CONSTRAINT scenarios_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: shipments shipments_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipments_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: simulation_events simulation_events_simulation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_events
    ADD CONSTRAINT simulation_events_simulation_id_fkey FOREIGN KEY (simulation_id) REFERENCES public.digital_twin_simulations(id) ON DELETE CASCADE;


--
-- Name: simulation_events simulation_events_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_events
    ADD CONSTRAINT simulation_events_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: simulation_snapshots simulation_snapshots_simulation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_snapshots
    ADD CONSTRAINT simulation_snapshots_simulation_id_fkey FOREIGN KEY (simulation_id) REFERENCES public.digital_twin_simulations(id) ON DELETE CASCADE;


--
-- Name: simulation_snapshots simulation_snapshots_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_snapshots
    ADD CONSTRAINT simulation_snapshots_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: stock_movements stock_movements_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id);


--
-- Name: stock_movements stock_movements_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: task_events task_events_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_events
    ADD CONSTRAINT task_events_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id) ON DELETE CASCADE;


--
-- Name: task_events task_events_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_events
    ADD CONSTRAINT task_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: tasks tasks_assigned_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_assigned_user_id_fkey FOREIGN KEY (assigned_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: tasks tasks_depends_on_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_depends_on_task_id_fkey FOREIGN KEY (depends_on_task_id) REFERENCES public.tasks(id) ON DELETE SET NULL;


--
-- Name: tasks tasks_destination_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_destination_location_id_fkey FOREIGN KEY (destination_location_id) REFERENCES public.warehouse_locations(id) ON DELETE SET NULL;


--
-- Name: tasks tasks_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: tasks tasks_order_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_order_item_id_fkey FOREIGN KEY (order_item_id) REFERENCES public.order_items(id) ON DELETE CASCADE;


--
-- Name: tasks tasks_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.items(id) ON DELETE CASCADE;


--
-- Name: tasks tasks_source_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_source_location_id_fkey FOREIGN KEY (source_location_id) REFERENCES public.warehouse_locations(id) ON DELETE SET NULL;


--
-- Name: tasks tasks_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: user_sessions user_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_warehouse_access user_warehouse_access_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_warehouse_access
    ADD CONSTRAINT user_warehouse_access_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_warehouse_access user_warehouse_access_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_warehouse_access
    ADD CONSTRAINT user_warehouse_access_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: warehouse_grid_cells warehouse_grid_cells_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_grid_cells
    ADD CONSTRAINT warehouse_grid_cells_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: warehouse_locations warehouse_locations_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_locations
    ADD CONSTRAINT warehouse_locations_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: warehouse_obstacles warehouse_obstacles_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_obstacles
    ADD CONSTRAINT warehouse_obstacles_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict Ic01NNBAmrTH0VAU9O31gBWZJgfvP6ccWzs6tmUEXhCxlTzmJ1DbAo8GtpvSKkN

