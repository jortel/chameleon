create sequence jeffseq;

create table
jeff
(
  id number(19) primary key
       using index tablespace users
     check (id > 0),
  name varchar(20) not null unique,
  age number default (1),
  info blob not null
);

create table hello
(
    id number(19) primary key,
    name varchar(10) not null,
    age number(2) not null default(to_char('don''t', 'b'))
         check ((age-1) > 0 and age = 0),
    date date default sysdate,
    mychar char not null check (mychar in ("y","n")),
    constraint latercheck check (id > 0),
    constraint name_pk primary key (name) using index tablespace [[ 4m_tbs ]]
    
)
;

/* 
This is my C comment 
*/

/* 
This is my (2nd) C comment //
*/

create global temporary table cache
(
   a char not null
) on commit delete rows;

create synonym jeffrey;
create or replace synonym scott for spud;
    
create TABLE jeff
(
   id         bigint primary key 
                 constraint nn not null
                 check (id >= 0 and id <= 100),
   created    timestamp default(CURRENT_TIMESTAMP) NOT NULL,
   age        number(2) not null
                 check (age > 0),
   column1    integer references scott(c1,c2),
   column2    CHAR(1)
                NOT NULL
                DEFAULT('N') 
                constraint column2_ck
                CHECK (column2 in ('1','2',"3"))
                constraint steve_fk references steve(c2) on delete cascade,
   column     varchar2(10)
                constraint steve_fk2 references steve(c2) on delete set null,

   constraint jeff_pk2 primary key (a, b),
   constraint jeff_fk2 foreign key (x, y) references phone (X,Y)
      on delete cascade,
   constraint age_uk unique (age)
)
enable row movement
parallel 5
;

alter table jeff
add
(
   A char,
   B varchar2(10) not null
);

alter table jeff add constraint jeff_added foreign key (x, y) references addon (X,Y);

alter table jeff drop constraint jeff_added;
alter table jeff drop column xyz;
alter table jeff rename column xyz to XYZ;
alter table jeff rename to JEFF;

alter table jeff
modify
(
   xyz varchar2(20) not null,
   zyx number
);

drop table jeff;

comment on table jeff is 'hello jeff';
comment on column jeff.a is 'hello (a) jeff';

create sequence jeff_seq;
        
create TABLE scott
(
  id number(26) primary key,
  id number(26) primary key using index tablespace InDTS,
  id number(26) constraint named_pk primary key,
  id number(26) constraint named_pk primary key using index tablespace InDTS
    default(0),
  age number(2) unique,
  age number(2) unique using index tablespace InDTS,
  age number(2) constraint named_uq unique,
  age number(2) constraint named_uq unique using index tablespace InDTS,
  c2 date
    constraint date_nn not null
    check (c2 <= sysdate),
  c3 number(4,2) unique,
  spud char check (spud in (a,b,c)),
  constraint scott_pk primary key (id),
  constraint scott_pk primary key (id) using index tablespace InDTS,
  constraint id_uq unique(id),
  constraint id_uq unique(id) using index tablespace InDTS
)
tablespace [[ 2m_tbs ]]
;

alter table scott parallel 4;
        
create sequence scott_seq start with 99;

create sequence date_seq start with 101010 order;
        
create TABLE steve (c1 number(26) default 0, c2 date );
        
CREATE unique INDEX scott_idx 
on scott (c1)
tablespace [[index_ts]] nologging;
        
create index bar on steve (c2) logging;

alter index bar parallel 2;

create table table (not_good smallint not null, b smallint);

insert into bla values (current_date-1000);
insert into xyz values (upper('hello'), to_char(sysdate), 3);
insert into names (a,b,c) values (nextval(abc),1,2,sysdate);
insert into jeff (a,b,c) values (abc_seq.nextval,current_timestamp,2,3);


create table T1
(
   a number(19)
);

alter table T1
add
(
   b char not null
);

alter table T1 rename column b to B;

