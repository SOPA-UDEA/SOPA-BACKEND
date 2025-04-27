-- CreateTable
CREATE TABLE "academic_program" (
    "id" SERIAL NOT NULL,
    "name" VARCHAR(150) NOT NULL,
    "code" VARCHAR(150) NOT NULL,
    "modalityAcademic" VARCHAR(150) NOT NULL,
    "headquarter" VARCHAR(150) NOT NULL,
    "version" INTEGER NOT NULL,
    "modalityId" INTEGER NOT NULL,
    "facultyId" INTEGER NOT NULL,
    "departmentId" INTEGER NOT NULL,

    CONSTRAINT "academic_program_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "academic_schedule" (
    "id" SERIAL NOT NULL,
    "semester" VARCHAR(150) NOT NULL,
    "pensumId" INTEGER NOT NULL,

    CONSTRAINT "academic_schedule_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "classroom" (
    "id" SERIAL NOT NULL,
    "capacity" INTEGER NOT NULL,
    "location" VARCHAR(150) NOT NULL,
    "ownDepartment" BOOLEAN,
    "virtualMode" BOOLEAN,

    CONSTRAINT "classroom_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "classroom_x_group" (
    "id" SERIAL NOT NULL,
    "groupId" INTEGER NOT NULL,
    "classroomId" INTEGER NOT NULL,
    "schedule" VARCHAR(150) NOT NULL,

    CONSTRAINT "classroom_x_group_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "department" (
    "id" SERIAL NOT NULL,
    "name" VARCHAR(150),
    "internalKey" VARCHAR(150),

    CONSTRAINT "department_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "faculty" (
    "id" SERIAL NOT NULL,
    "name" VARCHAR(150) NOT NULL,
    "internalKey" VARCHAR(150),

    CONSTRAINT "faculty_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "group" (
    "id" SERIAL NOT NULL,
    "groupSize" INTEGER NOT NULL,
    "modality" VARCHAR(150) NOT NULL,
    "code" INTEGER NOT NULL,
    "mirrorGroupId" INTEGER NOT NULL,
    "subjectId" INTEGER NOT NULL,
    "academicScheduleId" INTEGER NOT NULL,

    CONSTRAINT "group_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "group_x_professor" (
    "id" SERIAL NOT NULL,
    "groupId" INTEGER NOT NULL,
    "professorId" INTEGER NOT NULL,

    CONSTRAINT "group_x_professor_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "mirror_group" (
    "id" SERIAL NOT NULL,
    "name" VARCHAR(150),

    CONSTRAINT "mirror_group_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "modality" (
    "id" SERIAL NOT NULL,
    "IDE" VARCHAR(150),
    "name" VARCHAR(150) NOT NULL,

    CONSTRAINT "modality_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "pensum" (
    "id" SERIAL NOT NULL,
    "version" INTEGER NOT NULL,
    "academicProgramId" INTEGER NOT NULL,

    CONSTRAINT "pensum_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "professor" (
    "id" SERIAL NOT NULL,
    "name" VARCHAR(150) NOT NULL,
    "identification" VARCHAR(150),

    CONSTRAINT "professor_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "subject" (
    "id" SERIAL NOT NULL,
    "level" INTEGER NOT NULL,
    "fields" JSON NOT NULL,
    "code" VARCHAR NOT NULL,
    "credits" INTEGER NOT NULL,
    "weeklyHours" INTEGER NOT NULL,
    "weeks" INTEGER NOT NULL,
    "validable" BOOLEAN DEFAULT false,
    "enableable" BOOLEAN DEFAULT false,
    "preRequirements" JSON,
    "coRequirements" JSON,
    "creditRequirements" VARCHAR,
    "name" VARCHAR(150) NOT NULL,
    "type" BOOLEAN,
    "pensumId" INTEGER NOT NULL,

    CONSTRAINT "subject_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "academic_program" ADD CONSTRAINT "departmentId" FOREIGN KEY ("departmentId") REFERENCES "department"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "academic_program" ADD CONSTRAINT "facultyId" FOREIGN KEY ("facultyId") REFERENCES "faculty"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "academic_program" ADD CONSTRAINT "modalityId" FOREIGN KEY ("modalityId") REFERENCES "modality"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "academic_schedule" ADD CONSTRAINT "pensumId" FOREIGN KEY ("pensumId") REFERENCES "pensum"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "classroom_x_group" ADD CONSTRAINT "classroomId" FOREIGN KEY ("classroomId") REFERENCES "classroom"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "classroom_x_group" ADD CONSTRAINT "groupId" FOREIGN KEY ("groupId") REFERENCES "group"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "group" ADD CONSTRAINT "academicScheduleId" FOREIGN KEY ("academicScheduleId") REFERENCES "academic_schedule"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "group" ADD CONSTRAINT "mirrorGroupId" FOREIGN KEY ("mirrorGroupId") REFERENCES "mirror_group"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "group" ADD CONSTRAINT "subjectId" FOREIGN KEY ("subjectId") REFERENCES "subject"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "group_x_professor" ADD CONSTRAINT "groupId" FOREIGN KEY ("groupId") REFERENCES "group"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "group_x_professor" ADD CONSTRAINT "professorId" FOREIGN KEY ("professorId") REFERENCES "professor"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "pensum" ADD CONSTRAINT "academicProgramId" FOREIGN KEY ("academicProgramId") REFERENCES "academic_program"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "subject" ADD CONSTRAINT "pensumId" FOREIGN KEY ("pensumId") REFERENCES "pensum"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
