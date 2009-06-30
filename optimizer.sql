--
-- Copyright (c) 2008 Red Hat, Inc.
--
-- This software is licensed to you under the GNU General Public License,
-- version 2 (GPLv2). There is NO WARRANTY for this software, express or
-- implied, including the implied warranties of MERCHANTABILITY or FITNESS
-- FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
-- along with this software; if not, see
-- http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
-- 
-- Red Hat trademarks are not licensed under GPLv2. No permission is
-- granted to use or replicate Red Hat trademarks that are incorporated
-- in this software or its documentation. 
--

create table anonymous
(
  id   number(19) primary key not null unique
         using index tablespace users
         check (id > 0),
  name varchar(20) not null,
  age  number default (1)
       references person (a)
);

alter table anonymous parallel 1;


create table hello
(
    id number(19),
    name varchar(10) not null,
    age number(2) not null default(to_char('don''t', 'b'))
         check ((age-1) > 0 and age = 0),
    date date default sysdate,
    mychar char not null check (mychar in ('y','n')),
    u1 varchar2(10) not null,
    u2 varchar2(10) not null,
    constraint hello_pk primary key (id),
    constraint name_uq unique (name) using index tablespace jeff,
    constraint name_uq2 unique (u1,u2) using index tablespace jeff,
    constraint name_fk foreign key (name) references xyz (name) on delete cascade
)
;

create index hello_pk on hello (id)
  tablespace jeffID
  nologging;
create index name_uq2 on hello (u1,u2);
create index hello_U1 on hello (u1);
create index hello_U2 on hello (u2);
