# Hotel Property Management System

The Hotel Property Management System is a web-based application designed for hotels to manage work orders efficiently.
This system allows for the creation, assignment, and tracking of work orders within a hotel property. It also includes
integration with LINE Messaging API for communication with employees.


[![Build Status](https://github.com/watcharap0n/hotel-service/actions/workflows/workflow-app.yml/badge.svg)](https://github.com/watcharap0n/hotel-service/actions/workflows/workflow-app.yml)


### Table of Contents

- Features
- User Roles
- Installation
- Usage
- Messaging Integration
- Contributing
- License

## Features

## Work Order Management

#### The core functionality of the system includes the following features for work orders:

- Creation of work orders by multiple sources.
- Work order fields:
    - Work Order Number (Unique field)
    - Created By (User)
    - Assigned To (User)
    - Room
    - Started At
    - Finished At
    - Type (Cleaning, Maid Request, Technician Request, Amenity Request)
    - Status (Created, Assigned, In Progress, Done, Cancel)

## Role-Based Rules

Different user roles have specific rules for creating and managing work orders:

- Cleaning: Can be created by Maid Supervisor only, and has a proprietary status (Cancelled by Guest).

- Maid Request: Can be created by Maid Supervisor only, includes a free-text "Description" field.

- Technician Request: Can be created by guests or supervisors, with proprietary types for indicating defects in the
  room (Electricity, Air Con, Plumbing, Internet).

- Amenity Request: Can be created by guests only, with proprietary fields (Amenity Type, Quantity) for deducting
  inventory later.

## User Authentication

The system includes user authentication, allowing employees to log in with their respective roles.

Responsive UI
The user interface is designed to be responsive, ensuring a seamless experience across different devices.

## User Roles

The system has the following user roles:

1. Guest: Customers staying at the hotel. They can create Amenity Requests and Technician Requests.

2. Maid Supervisor: Employees responsible for maid services. They can create Cleaning and Maid Requests.

3. Technician: Employees responsible for technical maintenance. They can create Technician Requests.

4. Other Employees: Employees who are not supervisors. They can log in to the system to view work orders assigned to
   them.

`OpenAPI Hotel backend`
![Alt text](https://github.com/watcharap0n/hotel-service/blob/master/.github/assets/openapi1.png?raw=true "Title")
![Alt text](https://github.com/watcharap0n/hotel-service/blob/master/.github/assets/openapi2.png?raw=true "Title")

## Installation

To install and run the Hotel Property Management System locally, follow these steps

1. Clone the repository:


    git clone https://github.com/watcharap0n/hotel-service.git
    cd hotel-service

2. Build docker image and run container


    docker-compsoe up -d

3. Access the application api docs

    
    http://localhost:8080/api/docs

We appreciate your patience as we work on completing the frontend. If you have any suggestions or feedback, please feel free to [open an issue](https://github.com/watcharap0n/hotel-service/issues) to let us know how we can improve the system.

Stay tuned for updates on our progress!

## Messaging Integration
The Hotel Property Management System integrates with the LINE Messaging API for communication with employees. Here's how it works:

1. Supervisor Assignment: When a supervisor assigns work to an employee, the system sends a notification to the assigned employee via the LINE Messaging API.

2. Guest Requests: When a guest submits a request through the system, the system generates a response using LINE Messaging API Flex Messages and sends it to the LINE Official Account (OA) associated with this system. Guests receive responses on their LINE accounts.

## Contributing
Contributions to this project are welcome. Please follow the contribution guidelines for more information.

## License
This project is licensed under the MIT License.




