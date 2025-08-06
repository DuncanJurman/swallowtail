---
title: About Railway
description: Railway is a modern cloud deployment platform designed to help developers deploy instantly and scale apps effortlessly. Learn about our platform.
---

Railway is a deployment platform designed to streamline the software development life-cycle, starting with instant deployments and effortless scale, extending to CI/CD integrations and built-in observability.

## Deploying on Railway

Point Railway to your deployment source and let the platform handle the rest.

#### Flexible Deployment Sources
- **Code Repositories**: With or without Dockerfiles.  Railway will build an [OCI compliant image](https://opencontainers.org/) based on what you provide.
- **Docker Images**: Directly from Docker Hub, GitHub Container Registry, GitLab Container Registry, Microsoft Container Registry, or Quay.io.  We support public and private image registries.

#### Hassle-Free Setup
- **Sane Defaults**: Out of the box, your project is deployed with sane defaults to get you up and running as fast as possible.
- **Configuration Tuning**: When you're ready, there are plenty of knobs and switches to optimize as needed.

## Development Lifecycle

Software development extends far beyond code deployment.  Railway's feature set is tailor-made, and continuously evolving, to provide the best developer experience we can imagine.

#### Configuration Management
- **Variables & Secrets**: Easily manage configuration values and sensitive data with variable management tools.

#### Environment and Workflow
- **Environment Management**: Create both static and ephemeral environments to create workflows that complement your processes.
- **Orchestration & Tooling**: Build Railway into any workflow using our CLI or API.

#### Deployment Monitoring
- **Observability**: Keep a pulse on your deployments with Railway's built-in observability tools.

## Operational Model

Railway operates with an emphasis on reliability and transparency. We utilize a combination of alerting tools, internal systems, and operational procedures to maintain high uptime.  Read more about product philosophy and maturity [here](/maturity/philosophy).

## Book a Demo

Looking to adopt Railway for your business?  We'd love to chat!  [Click here to book some time with us](https://cal.com/team/railway/work-with-railway?duration=30).


---
title: Best Practices
description: Learn the best practices to maximize performance, efficiency, and scalability of your apps on Railway.
---
{/**
To keep consistency we want each topic to follow the same convention -
- What?
- When?
- Do X.
- Why?
- Image.
*/}


Railway is a highly versatile platform, offering various ways to use it, though some may be less optimal than others for most use cases. These topics aim to help you maximize both your potential and the platform's capabilities.

## Use Private Networking When Possible

[Private networking](/reference/private-networking) allows services within a [project](/overview/the-basics#project--project-canvas) to communicate internally without the need to expose them [publicly](/guides/public-networking), while also providing faster communication and increased throughput.

When configuring environment variables in your service to reference domains or URLs of other services, ensure you use the private versions of these variables, such as `RAILWAY_PRIVATE_DOMAIN` or `DATABASE_URL`.

Using the private network enables communication between services within the same project without incurring service-to-service egress costs, which is particularly beneficial when interacting with databases or other internal services.

<Image src="https://res.cloudinary.com/railway/image/upload/v1725659271/docs/best-practices/use_private_networking_son2xp.png"
alt="screenshot of a service showing the use of private networking via reference variables"
layout="intrinsic"
width={1048} height={818} quality={100} />

<span style={{'font-size': "0.9em"}}>Screenshot showing the use of the `RAILWAY_PRIVATE_DOMAIN` [variable](/reference/variables#railway-provided-variables) being used via [referencing](/guides/variables#reference-variables).</span>

## Deploying Related Services Into the Same Project

In Railway, a [project](/overview/the-basics#project--project-canvas) serves as a container for organizing infrastructure. It can encompass an application stack, a group of [services](/overview/the-basics#services), or even multiple service groups.

If you're about to head back to the [dashboard](/overview/the-basics#dashboard--projects) to deploy another service like a database, there's a quicker way - look for the `Create` button at the top right of the Project canvas. This shortcut allows you to add new services directly to your current project.

There are a few key advantages of keeping related services within the same project -

- **Private networking** - The private network is scoped to a single environment within a project, having all related services within a single project will allow you to use private networking for faster networking along with no egress fees for service-to-service communication.

- **Project clutter** - Deploying a new service or database as an entire project will quickly become overwhelming and clutter your dashboard.

- **Variable management** - Variables can be referenced between services within a project, reducing redundancy and making it easier to manage instead of having to manually copy variables between services.

<Image src="https://res.cloudinary.com/railway/image/upload/v1725659271/docs/best-practices/related_services_in_a_project_mtxuis.png"
alt="screenshot of the project canvas showing multiple linked services"
layout="intrinsic"
width={1048} height={818} quality={100} />

<span style={{'font-size': "0.9em"}}>Screenshot showing related services within a project and their connection links.</span>

## Use Reference Variables Where Applicable

[Reference variables](/guides/variables#reference-variables) allow you to dynamically reference another variable, either from a variable set on the current [service](/overview/the-basics#services) or from another service in the same [project](/overview/the-basics#project--project-canvas).

Rather than manually copying, pasting, and hard-coding variables like a public domain or those from another service, you can use reference variables to build them dynamically. Example `VITE_BACKEND_HOST=${{Backend.RAILWAY_PUBLIC_DOMAIN}}`

This approach is better than hard-coding variables, as it keeps your variable values in sync. Change your [public domain](/reference/public-domains)? The variable updates. Change your [TCP proxy](/reference/tcp-proxy)? The variable updates.

<Image src="https://res.cloudinary.com/railway/image/upload/v1725659271/docs/best-practices/use_reference_variables_h8qtik.png"
alt="screenshot of a service showing the use of reference variables"
layout="intrinsic"
width={1048} height={818} quality={100} />

<span style={{'font-size': "0.9em"}}>Screenshot showing a reference variable used to reference the Backend's domain.</span>

---
title: Using Config as Code
description: Learn how to manage and deploy apps on Railway using config as code with toml and json files.
---

Railway supports defining the configuration for a single deployment in a file
alongside your code in a `railway.toml` or `railway.json` file.

Everything in the build and deploy sections of the service settings page can be specified in this configuration file.

The settings in the dashboard will not be updated with the settings defined in
code. Configuration defined in code will always override values from the
dashboard.

## Toml vs Json

The format you use for your config-as-code (toml or json) file is entirely dependent on preference, and the resulting behavior in Railway is the same no matter which you choose.

For example, these configuration definitions are equivalent:


<div style={{ display: 'flex', flexDirection: 'row', gap: '5px', fontSize: '0.9em', alignItems: 'stretch' }}>
    <div style={{ flex: '1 1 50%', overflow: 'auto', minWidth: '200px', maxWidth: '350px' }}>
        ```toml
        [build]
        builder = "nixpacks"
        buildCommand = "echo building!"

        [deploy]
        preDeployCommand = ["npm run db:migrate"]
        startCommand = "echo starting!"
        healthcheckPath = "/"
        healthcheckTimeout = 100
        restartPolicyType = "never"





        --
        ```
        <p style={{ marginTop: '-0.2em', fontSize: '0.8em', opacity: '0.6' }}>A `railway.toml` file</p>
    </div>
    <div style={{ flex: '1 1 50%', overflow: 'auto', minWidth: '200px', maxWidth: '350px' }}>
        ```json
        {
          "$schema": "https://railway.com/railway.schema.json",
          "build": {
            "builder": "NIXPACKS",
            "buildCommand": "echo building!"
            },
          "deploy": {
            "preDeployCommand": ["npm run db:migrate"],
            "startCommand": "echo starting!",
            "healthcheckPath": "/",
            "healthcheckTimeout": 100,
            "restartPolicyType": "never"
            }
        }

        ```
        <p style={{ marginTop: '-0.2em', fontSize: '0.8em', opacity: '0.6' }}>A `railway.json` file</p>
    </div>
</div>

## JSON Schema

You can find an always up-to-date [JSON schema](https://json-schema.org/) at [railway.com/railway.schema.json](https://railway.com/railway.schema.json).

If you include it in your `railway.json` file, many editors (e.g. VSCode) will provide autocomplete and documentation.

```json
{
  "$schema": "https://railway.com/railway.schema.json"
}
```


## Understanding Config Source

On a service's deployment details page, all the settings that a deployment went out with are shown.

For settings that come from a configuration file, there is a file icon. Hovering over the icon will show exactly what part of the file the values originated from.

<Image
src="https://res.cloudinary.com/railway/image/upload/v1743195106/docs/configuration_emrjth.png"
alt="Screenshot of Deployment Details Pane"
layout="responsive"
width={1200} height={631} quality={100} />


## Using a Custom Config as Code File

You can use a custom config file by setting it on the service settings page. The file is relative to your app source.

<Image
src="https://res.cloudinary.com/railway/image/upload/v1743195631/docs/config-file_f1wf32.png"
alt="Screenshot of Rollback Menu"
layout="responsive"
width={1200} height={374} quality={100} />

## Configurable Settings

Find a list of all of the configurable settings in the [config as code reference page](/reference/config-as-code#configurable-settings).