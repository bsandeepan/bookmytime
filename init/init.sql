-- create UserSettings table
DROP TABLE IF EXISTS public."UserSettings";
CREATE TABLE public."UserSettings"
(
    "UserId" character varying(10) COLLATE pg_catalog."default" NOT NULL,
    "Duration" smallint NOT NULL DEFAULT 60,
    "Timezone" character varying(40) NOT NULL,
    "MaxCalenderDays" smallint NOT NULL DEFAULT 30,
    "UpdatedAt" timestamp without time zone NOT NULL,
    "AvailabilityRules" jsonb NOT NULL,
    CONSTRAINT "UserIdPK" PRIMARY KEY ("UserId")
);

ALTER TABLE IF EXISTS public."UserSettings"
    OWNER to postgres;

-- create Events table
DROP TABLE IF EXISTS public."Events";
CREATE TABLE IF NOT EXISTS public."Events"
(
    "EventId" uuid NOT NULL,
    "OrganizerId" character varying(10) COLLATE pg_catalog."default" NOT NULL,
    "AttendeeId" character varying(10) COLLATE pg_catalog."default" NOT NULL,
    "StartTime" timestamp without time zone NOT NULL,
    "Duration" smallint NOT NULL,
    "CreatedAt" timestamp without time zone NOT NULL,
    "UpdatedAt" timestamp without time zone NOT NULL,
    "Notes" text COLLATE pg_catalog."default",
    "Status" character varying(10) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "Events_pkey" PRIMARY KEY ("EventId"),
    CONSTRAINT "AttendeeIdFK" FOREIGN KEY ("AttendeeId")
        REFERENCES public."UserSettings" ("UserId") MATCH FULL
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT "OrganizerIdFK" FOREIGN KEY ("OrganizerId")
        REFERENCES public."UserSettings" ("UserId") MATCH FULL
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."Events"
    OWNER to postgres;

-- Insert pre-existing users
INSERT INTO public."UserSettings"("UserId", "Timezone", "UpdatedAt", "AvailabilityRules")
	VALUES 	('US00000001', 'Asia/Kolkata', '2024-06-14 07:02:14.345', '[{"Day":"monday","Hours":[["08:00","11:00"],["15:30","17:00"],["19:00","21:00"]]},{"Day":"tuesday","Hours":[["08:00","14:00"],["15:30","16:00"]]},{"Day":"friday","Hours":[["08:00","20:00"]]}]'),
			('US00000002', 'CET', '2024-06-14 11:34:17.146', '[{"Day":"monday","Hours":[["08:00","11:00"],["15:30","17:00"],["19:00","21:00"]]},{"Day":"tuesday","Hours":[["08:00","13:00"],["15:30","16:00"]]},{"Day":"wednesday","Hours":[["08:00","18:00"]]},{"Day":"friday","Hours":[["08:00","20:00"]]}]');
-- Insert pre-existing events
INSERT INTO public."Events"("EventId", "OrganizerId", "AttendeeId", "StartTime", "Duration", "CreatedAt", "UpdatedAt", "Notes", "Status")
	VALUES (gen_random_uuid(), 'US00000001', 'US00000002', '2024-06-25 06:30:00.000', 60, '2024-06-14 14:02:14.345', '2024-06-14 14:02:14.345', 'this is a test event', 'CREATED');
