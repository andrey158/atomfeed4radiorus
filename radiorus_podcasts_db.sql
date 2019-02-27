--
-- PostgreSQL database dump
--

-- Dumped from database version 10.6 (Ubuntu 10.6-1.pgdg16.04+1)
-- Dumped by pg_dump version 10.6 (Ubuntu 10.6-1.pgdg16.04+1)

-- Started on 2019-02-27 19:42:53 MSK

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 2891 (class 1262 OID 16385)
-- Name: radiorus_podcasts; Type: DATABASE; Schema: -; Owner: radiorus
--

CREATE DATABASE radiorus_podcasts WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'ru_RU.utf8' LC_CTYPE = 'ru_RU.utf8';


ALTER DATABASE radiorus_podcasts OWNER TO radiorus;

\connect radiorus_podcasts

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 1 (class 3079 OID 13003)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2893 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 197 (class 1259 OID 16396)
-- Name: audio_records; Type: TABLE; Schema: public; Owner: radiorus
--

CREATE TABLE public.audio_records (
    podcast_id integer NOT NULL,
    episode_id integer NOT NULL,
    audio_id integer NOT NULL,
    title text,
    url text,
    length text
);


ALTER TABLE public.audio_records OWNER TO radiorus;

--
-- TOC entry 196 (class 1259 OID 16386)
-- Name: episodes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.episodes (
    podcast_id integer NOT NULL,
    id integer NOT NULL,
    title text,
    description text,
    url text,
    image_url text,
    published timestamp without time zone
);


ALTER TABLE public.episodes OWNER TO postgres;

--
-- TOC entry 2895 (class 0 OID 0)
-- Dependencies: 196
-- Name: COLUMN episodes.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.episodes.id IS 'id эпизода';


--
-- TOC entry 2896 (class 0 OID 0)
-- Dependencies: 196
-- Name: COLUMN episodes.title; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.episodes.title IS 'Название эпизода';


--
-- TOC entry 2897 (class 0 OID 0)
-- Dependencies: 196
-- Name: COLUMN episodes.url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.episodes.url IS 'Ссылка на эпизод';


--
-- TOC entry 2898 (class 0 OID 0)
-- Dependencies: 196
-- Name: COLUMN episodes.published; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.episodes.published IS 'Дата выпуска';


--
-- TOC entry 198 (class 1259 OID 16423)
-- Name: podcasts; Type: TABLE; Schema: public; Owner: radiorus
--

CREATE TABLE public.podcasts (
    id integer NOT NULL,
    title text,
    logo_url text
);


ALTER TABLE public.podcasts OWNER TO radiorus;

--
-- TOC entry 2761 (class 2606 OID 16408)
-- Name: audio_records audio_records_pkey; Type: CONSTRAINT; Schema: public; Owner: radiorus
--

ALTER TABLE ONLY public.audio_records
    ADD CONSTRAINT audio_records_pkey PRIMARY KEY (audio_id);


--
-- TOC entry 2759 (class 2606 OID 16393)
-- Name: episodes episodes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.episodes
    ADD CONSTRAINT episodes_pkey PRIMARY KEY (podcast_id, id);


--
-- TOC entry 2763 (class 2606 OID 16430)
-- Name: podcasts podcasts_pkey; Type: CONSTRAINT; Schema: public; Owner: radiorus
--

ALTER TABLE ONLY public.podcasts
    ADD CONSTRAINT podcasts_pkey PRIMARY KEY (id);


--
-- TOC entry 2764 (class 2606 OID 16402)
-- Name: audio_records episodes; Type: FK CONSTRAINT; Schema: public; Owner: radiorus
--

ALTER TABLE ONLY public.audio_records
    ADD CONSTRAINT episodes FOREIGN KEY (podcast_id, episode_id) REFERENCES public.episodes(podcast_id, id);


--
-- TOC entry 2894 (class 0 OID 0)
-- Dependencies: 197
-- Name: TABLE audio_records; Type: ACL; Schema: public; Owner: radiorus
--

GRANT ALL ON TABLE public.audio_records TO atom_feeder;


--
-- TOC entry 2899 (class 0 OID 0)
-- Dependencies: 196
-- Name: TABLE episodes; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.episodes TO atom_feeder;


--
-- TOC entry 2900 (class 0 OID 0)
-- Dependencies: 198
-- Name: TABLE podcasts; Type: ACL; Schema: public; Owner: radiorus
--

GRANT ALL ON TABLE public.podcasts TO atom_feeder;


-- Completed on 2019-02-27 19:42:53 MSK

--
-- PostgreSQL database dump complete
--

