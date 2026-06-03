create database shoes_shop2;
use shoes_shop2;
create table Roles(
RoleID int primary key auto_increment,
name varchar(100));
select * from Roles;

create table Users(
UserID int primary key auto_increment,
FIO varchar(255),
Login varchar(50),
Password varchar(50),
RoleID int,
foreign key (RoleID) references Roles(RoleID)
);
select * from Users;

create table Categories(
CategoryID int primary key auto_increment,
Name varchar(50));
select * from Categories;

create table Manufacturers(
ManufID int primary key auto_increment,
Name varchar(50));
select * from Manufacturers;

create table Suppliers(
SupID int primary key auto_increment,
Name varchar(50));
select * from Suppliers;

create table PostPoints(
PostID int primary key auto_increment,
PostCode varchar(50),
City varchar(50),
Street varchar(50),
Building varchar(50));
select * from PostPoints;

create table StatusOrder(
StatusID int primary key auto_increment,
Name varchar(50));
select * from StatusOrder;

create table Products(
ProductID int primary key auto_increment,
Name varchar(50),
CategoryID int,
Description varchar(255),
ManufID int,
SupID int,
Price float,
Unit varchar(50),
Quantity int,
Discount int,
Image varchar(255),
Article varchar(50),
foreign key (CategoryID) references Categories(CategoryID),
foreign key (ManufID) references Manufacturers(ManufID),
foreign key (SupID) references Suppliers(SupID) );
select * from Products;


create table Orders(
OrderID int primary key auto_increment,
Date_order varchar(50),
Delivery_date varchar(50),
PostID int,
UserId int,
Code int,
StatusID int,
foreign key (PostId) references PostPoints(PostID),
foreign key (UserID) references Users(UserID),
foreign key (StatusID) references StatusOrder(StatusID));
select * from Orders;

create table ProductInOrders(
ProductInOrdersId int primary Key auto_increment,
amount varchar(45),
OrderID int,
ProductID int,
foreign key (OrderID) references Orders (OrderID),
foreign key (ProductID) references Products(ProductID)
);
select * from ProductInOrders;


