# Connections Module of a Social Network

This is an attempt to provide a production-ready design and architecture for the connections module of a social network.

A reference implementation is also included.

The detailed problem statement is available [here](https://gist.github.com/rootAvish/cc5c7177ce0411a5da11d1c99509b22e).

#### Relevant assumptions (product)
* conventions: the overall social network is called `SocialApp` and our connections module is named `ConnectionsModule`.
* `ConnectionsModule` is to be built from scratch, and is expected to scale up to ~100k users.
* around 30% of the total users are expected to be active at any time, and peak engagement might be ~70% users.
* the product in this phase is geographically restricted to people of South Asia.

#### Relevant assumptions (engineering)
* `ConnectionsModule` will operate as an end-to-end independent component with tight contracts.
* `ConnectionsModule` will expose web services around its core business functionality.
* the services are to be designed for internal, programmatic access rather than user-facing.
* the design and deployment of `ConnectionsModule` is not influenced or constrained by any larger dependencies/conventions/feature-sets of SocialApp.


# Design Document

### Overview
ConnnectionsModule is an independent SocialApp component that manages all connections and recommendations. This document lays out the proposed design for v1 of ConnectionsModule.

### Goals
* enable users getting created and updated within SocialApp.
* enable users adding/removing connections within SocialApp.
* enable management and serving of users' metadata: 
* profile information
    * connected users
    * recommended users
    * act as the sole custodian of this metadata, charged with keeping it safe and secure.

### Non-Goals
* manage Authentication and Authorization flows.
* manage security workflows like encryption/decryption of profile information between components.
* generate relevant recommendations for users.
* allow a user to be deleted from SocialApp.
* enable offline workflows.

### Functionality
The system should support the following actions:
1. creating a user
2. updating a user
3. adding a connection
4. removing a connection
5. adding multiple connections in a batch mode.
6. checking if a user is connected to another user
7. getting a user's profile information
8. getting a user's connections
9. getting a user's recommendations
10. adding a user's recommendations
11. deleting a user's recommendations

The system should expose RESTful web APIs for actions 1-9.

### SLA's:
* for all APIs, the request-response cycle should be within acceptable latency standards ( ~500 ms)
* the system should have an uptime of 99%
* the system should support ~100k total users without performance variations.
* the system should support ~5k connections/friends per user without performance variations.
* the system should support ~70k simultaneous active users without performance variations.
* the above SLAs should be true for any user located in our target geographical range (South Asia).

### Proposed Solution
* Since the overarching goal is to build the backend for a web app, the flows are data-driven. Our design therefore loosely follows the MVC design pattern which suits these flows.
* The system will have 3 layers: 
    * The resources layer:  This layer is the only "public" face of the system. All of the APIs/web services are defined here. This layer should have as little business logic as possible, and instead try to delegate the heavy lifting to the layers below. It is the responsibility of this layer to:
        * handle any security concerns due to abuse
        *  adhere to well-established UX principles
        * honor the SLAs defined above
    * A definition which makes sense for the business domain might not be suitable from the client perspective. There are considerations of network bandwidth, excess chattiness and security at play. The resources layer should therefore define its own data models that will be used in API responses. It should also provide a translator to manage transformations between the business entity and the web resource.
    * controller: this acts as the interface between the view and the models. All the business logic and workflows are defined here. It is the responsibility of the controller to expose specific functionality that makes sense to the client. To execute a functionality, it 1) uses its business-awareness to come up with a multi-step procedure 2) asks the models to carry out actual CRUD on entities, in the order it wants, and keeps track of the results 3) optionally exposes the results to the view.
    * models: all the data models (from a domain/business point of view) are defined here. A data model consists of the business entity itself (preferably defined as a class), as well as a contract through which CRUD operations will be supported on that entity, or a collection of such entities. A model is the deepest layer and has no awareness of the controller and views.
    * A definition which makes sense for the business domain might not be suitable from the database schema perspective . To enable decoupling these two, we propose an ORM layer which will manage the translation between the models and the database definitions. This arrangement gives us another advantage: we can cold-swap any data storage layer provided we can adhere to the CRUD contract defined by the model. All of this does come at the cost of increasing complexity though.
* The system will also support long-running operations via an offline tasks queue and workers.

### Class Diagram
![Class Diagram](https://github.com/abhishekpathak/connections-module/blob/master/ClassDiagram.png)

### User Interface
None.

### API Interface
OpenApi 2.0 spec available [here](https://github.com/abhishekpathak/connections-module/blob/master/swagger/swagger.yaml).

### Databases and schemas
* A fully relational schema would be to create a table for the users, another one for the connections, and another for the recommendations. We will have ACID guarantees but lookups like 'find all users connected to this user' would be very expensive.
* Social relationships as naturally modelled as graphs. We could move the connections data to a graph database like Neo4j to model the users as nodes and connections as edges.
* User profile and recommendations could be kept in an RDBMS like MySQL or Postgres.
* For testing, an in-memory object store like Redis could work, but we would lose ACID guarantees and the repository code would have to handle these cases.
* Sample schema for MySQL:

```sql
CREATE TABLE user_profiles
  (
     user_id VARCHAR(255) NOT NULL PRIMARY KEY,
     NAME    VARCHAR(255) NOT NULL,
     email   VARCHAR(255) NOT NULL,
     college VARCHAR(255),
  ) 


CREATE TABLE recommendations
  (
     id                  VARCHAR(255) NOT NULL PRIMARY KEY,
     user_id             VARCHAR(255) NOT NULL,
     recommended_user_id VARCHAR(255) NOT NULL
  )

CREATE INDEX idx_user ON recommendations (user_id)
```
        
### Tools and Frameworks:
* #### proposed
    * python 3.7 as the coding language
        * allows for rapid prototyping
        * brilliant ecosystem of libraries and frameworks
    * flask and flask-restful for building web services
        * more modular
    * ORM: SQLAlchemy
    * object translation library: Marshmallow
    * Celery as a distributed task queue with Redis as the message broker
* #### alternatives considered
    * Java as the coding language
        * strongly typed so better refactoring/compiler hinting
        * well-established concurrency model can be leveraged for better throughput
        * similar ecosystem of 3rd party libraries and frameworks
        * the JVM has rich tuning and monitoring capabilities.
    * Django as the web framework
        * bundles everything - auth, ORM, object translation, design conventions etc.        
    
### Architecture Diagram
![Architecture Diagram](https://github.com/abhishekpathak/connections-module/blob/master/ArchitectureDiagram.png)

### Scaling strategies
* horizontal scaling, load balanced
* shared storage (databases)
* shared, distributed task queue for all long-running tasks (for example, batch operations)
* sticky sessions to be enabled through tokens and load balancer
* NoSQL graph databases to model users and their connections. RDBMS for everything else.
* Containers(docker) + Orchestrator(Kubernetes) based deployment for easy scaling.

### Speedup strategies
* caching to be done via a simple cache-aside strategy for v1. Redis preferred as a cache store due to its data type flexibility.
* co-located application servers + databases + cache to reduce the network latency.
* use CDN for static content. A pull CDN is preferred.
* this system will have read-heavy loads. The RDBMS will have a master-slave architecture with high number of read-only slaves.
* non-ACID databases for faster reads. The system can get by with eventual consistency.

### Monitoring and Alerting
* Metrics to monitor:
    * web services
        * QPS for web services
        * avg latency for web services
    * databases
        * database operations per second
        * slow queries
    * hardware    
        * health checks via heartbeats
        * spikes (>90%) in RAM and CPU
* Set up alerts for metrics above threshold.

### Failover/HA strategies
* Multiple load balancers with a CDN should guarantee high availability.
* No state should be stored on local hardware in the application.
* Since it models a real-world social network, the data for `ConnectionsModule` needs to have high safety and availability.
    * master-slave RDBMS architecture for live replication of production data
    * geo-distributed databases
    * regular, automated backups of databases

### Deployment strategies
* On-prem preferred over cloud:
    * We don't expect sudden variations in traffic like News websites during an important event, or E-commerce websites during sale events.
    * Rapid upscaling and downscaling is not a goal to solve for, instead a steady growth in traffic is expected.
    * Security and privacy concerns: ConnectionsModule stores personal and private data of its users. A private data center will give us better control over our security policies and guarantees we can provide.
* Containers like docker or LXE can be used for easy deployment and easy virtualization on different grades of bare-metal servers.
* Kubernetes can be used to automatically orchestrate deployments and scale the platform as needed.

### Testability and code hygiene
* A test (unit + integration) coverage of 60% (or better) allows us a fair bit of regression while adding new features.
* guidelines: for easy testability
    * prefer composition over inheritance, and use dependency injections when creating classes.
    * TDD is encouraged
    * design loosely coupled systems for easy mocking
    * make heavy use of logging. log all transactions between application layers (debug).
* guidelines: for easily maintainable code
    * use [PEP-8 naming conventions](https://www.python.org/dev/peps/pep-0008/#naming-conventions) for classes, methods, variables, constants, functions etc
    * use [Google's python style guide](http://google.github.io/styleguide/pyguide.html) for code documentation.
    * use [Angular's git commit message conventions](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-guidelines).
    * APIs should be influenced by [Microsoft's API design guidelines](https://github.com/Microsoft/api-guidelines/blob/master/Guidelines.md).
* guidelines: code reviews and pull requests
    * ensure that there are no TODOs or commented blocks. 
    * Any TODO intended to be tackled later should be added as a github issue.
    * mention if it added/deleted a migration
    * mention if this feature warrants external documentation

### Engineering Milestones
* Start Date: Sep 17, 2019
* Milestone 1: New system MVP running in dark-mode: Sep 22, 2019
* Milestone 2: Production
    * scale: <= ~100k total users
    * codebase metrics: TBD
