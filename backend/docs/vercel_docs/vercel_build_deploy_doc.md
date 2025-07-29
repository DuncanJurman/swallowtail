# Builds

Vercel automatically performs a build every time you deploy your code, whether you're pushing to a Git repository, importing a project via the dashboard, or using the [Vercel CLI](/docs/cli). This process compiles, bundles, and optimizes your application so it's ready to serve to your users.

## [Build infrastructure](#build-infrastructure)

When you initiate a build, Vercel creates a secure, isolated virtual environment for your project:

*   Your code is built in a clean, consistent environment
*   Build processes can't interfere with other users' applications
*   Security is maintained through complete isolation
*   Resources are efficiently allocated and cleaned up after use

This infrastructure handles millions of builds daily, supporting everything from individual developers to large enterprises, while maintaining strict security and performance standards.

Most frontend frameworks—like Next.js, SvelteKit, and Nuxt—are auto-detected, with defaults applied for Build Command, Output Directory, and other settings. To see if your framework is included, visit the [Supported Frameworks](/docs/frameworks) page.

## [How builds are triggered](#how-builds-are-triggered)

Builds can be initiated in the following ways:

1.  Push to Git: When you connect a GitHub, GitLab, or Bitbucket repository, each commit to a tracked branch initiates a new build and deployment. By default, Vercel performs a _shallow clone_ of your repo (`git clone --depth=10`) to speed up build times.
    
2.  Vercel CLI: Running `vercel` locally deploys your project. By default, this creates a preview build unless you add the `--prod` flag (for production).
    
3.  Dashboard deploy: Clicking Deploy in the dashboard or creating a new project also triggers a build.
    

## [Build customization](#build-customization)

Depending on your framework, Vercel automatically sets the Build Command, Install Command, and Output Directory. If needed, you can customize these in your project's Settings:

1.  Build Command: Override the default (`npm run build`, `next build`, etc.) for custom workflows.
    
2.  Output Directory: Specify the folder containing your final build output (e.g., `dist` or `build`).
    
3.  Install Command: Control how dependencies are installed (e.g., `pnpm install`, `yarn install`) or skip installing dev dependencies if needed.
    

To learn more, see [Configuring a Build](/docs/deployments/configure-a-build).

## [Skipping the build step](#skipping-the-build-step)

For static websites—HTML, CSS, and client-side JavaScript only—no build step is required. In those cases:

1.  Set Framework Preset to Other.
2.  Leave the build command blank.
3.  (Optionally) override the Output Directory if you want to serve a folder other than `public` or `.`.

## [Monorepos](#monorepos)

When working in a monorepo, you can connect multiple Vercel projects within the same repository. By default, each project will build and deploy whenever you push a commit. Vercel can optimize this by:

1.  Skipping unaffected projects: Vercel automatically detects whether a project's files (or its dependencies) have changed and skips deploying projects that are unaffected. This feature reduces unnecessary builds and doesn't occupy concurrent build slots. Learn more about [skipping unaffected projects](/docs/monorepos#skipping-unaffected-projects).
    
2.  Ignored build step: You can also write a script that cancels the build for a project if no relevant changes are detected. This approach still counts toward your concurrent build limits, but may be useful in certain scenarios. See the [Ignored Build Step](/docs/project-configuration/git-settings#ignored-build-step) documentation for details.
    

For monorepo-specific build tools, see:

*   [Turborepo](/docs/monorepos/turborepo)
*   [Nx](/docs/monorepos/nx)

## [Concurrency and queues](#concurrency-and-queues)

When multiple builds are requested, Vercel manages concurrency and queues for you:

1.  Concurrency Slots: Each plan has a limit on how many builds can run at once. If all slots are busy, new builds wait until a slot is free.
    
2.  Branch-Based Queue: If new commits land on the same branch, Vercel skips older queued builds and prioritizes only the most recent commit. This ensures that the latest changes are always deployed first.
    
3.  On-Demand Concurrency: If you need more concurrent build slots or want certain production builds to jump the queue, consider enabling [On-Demand Concurrent Builds](/docs/deployments/managing-builds#on-demand-concurrent-builds).
    

## [Environment variables](#environment-variables)

Vercel can automatically inject environment variables such as API keys, database connections, or feature flags during the build:

1.  Project-Level Variables: Define variables under Settings for each environment (Preview, Production, or any custom environment).
    
2.  Pull Locally: Use `vercel env pull` to download environment variables for local development. This command populates your `.env.local` file.
    
3.  Security: Environment variables remain private within the build environment and are never exposed in logs.
    

## [Ignored files and folders](#ignored-files-and-folders)

Some files (e.g., large datasets or personal configuration) might not be needed in your deployment:

*   Vercel automatically ignores certain files (like `.git`) for performance and security.
*   You can read more about how to specify [ignored files and folders](/docs/builds/build-features#ignored-files-and-folders).

## [Build output and deployment](#build-output-and-deployment)

Once the build completes successfully:

1.  Vercel uploads your build artifacts—static files, Vercel Functions, and other assets—to the Edge Network.
2.  A unique deployment URL is generated for Preview or updated for Production domains.
3.  Logs and build details are available in the Deployments section of the dashboard.

If the build fails or times out, Vercel provides diagnostic logs in the dashboard to help you troubleshoot. For common solutions, see our [build troubleshooting](/docs/deployments/troubleshoot-a-build) docs.

## [Build infrastructure](#build-infrastructure)

Behind the scenes, Vercel manages a sophisticated global infrastructure that:

*   Creates isolated build environments on-demand
*   Handles automatic regional failover
*   Manages hardware resources efficiently
*   Pre-warms containers to improve build start times
*   Synchronizes OS and runtime environments with your deployment targets

## [Limits and resources](#limits-and-resources)

Vercel enforces certain limits to ensure reliable builds for all users:

*   Build timeout: The maximum build time is 45 minutes. If your build exceeds this limit, it will be terminated, and the deployment fails.
    
*   Build cache: Each build cache can be up to 1 GB. The [cache](/docs/deployments/troubleshoot-a-build#caching-process) is retained for one month. Restoring a build cache can speed up subsequent deployments.
    
*   Container resources: Vercel creates a [build container](/docs/builds/build-image) with different resources depending on your plan:
    
    |  | Hobby | Pro | Enterprise |
    | --- | --- | --- | --- |
    | Memory | 8192 MB | 8192 MB | Custom |
    | Disk Space | 13 GB | 13 GB | Custom |
    | CPUs | 2 | 4 | Custom |
    

For more information, visit [Build Container Resources](/docs/deployments/troubleshoot-a-build#build-container-resources) and [Cancelled Builds](/docs/deployments/troubleshoot-a-build#cancelled-builds-due-to-limits).

## [Learn more about builds](#learn-more-about-builds)

To explore more features and best practices for building and deploying with Vercel:

*   [Configure your build](/docs/builds/configure-a-build): Customize commands, output directories, environment variables, and more.
*   [Troubleshoot builds](/docs/deployments/troubleshoot-a-build): Get help with build cache, resource limits, and common errors.
*   [Manage builds](/docs/builds/managing-builds): Control how many builds run in parallel and prioritize critical deployments.
*   [Working with Monorepos](/docs/monorepos): Set up multiple projects in a single repository and streamline deployments.

## [Pricing](#pricing)

Manage and Optimize pricing
| 
Metric

 | 

Description

 | 

Priced

 | 

Optimize

 |
| --- | --- | --- | --- |
| [Build Time](/docs/builds/managing-builds#managing-build-time) | The amount of time your Deployments have spent being queued or building | [Additional concurrent builds](/docs/pricing#managed-infrastructure-billable-resources) | [Learn More](/docs/builds/managing-builds#managing-build-time) |
| [Number of Builds](/docs/builds/managing-builds#number-of-builds) | How many times a build was issued for one of your Deployments | No | N/A |

Last updated on July 18, 2025

# Build Features for Customizing Deployments

Vercel provides the following features to customize your deployments:

*   [Private npm packages](#private-npm-packages)
*   [Ignored files and folders](#ignored-files-and-folders)
*   [Special paths](#special-paths)
*   [Git submodules](#git-submodules)

## [Private npm packages](#private-npm-packages)

When your project's code is using private `npm` modules that require authentication, you need to perform an additional step to install private modules.

To install private `npm` modules, define `NPM_TOKEN` as an [Environment Variable](/docs/environment-variables) in your project. Alternatively, define `NPM_RC` as an [Environment Variable](/docs/environment-variables) in the contents of the project's npmrc config file that resides at the root of the project folder and is named `~/.npmrc`. This file defines the config settings of `npm` at the level of the project.

To learn more, check out the [guide here](/guides/using-private-dependencies-with-vercel) if you need help configuring private dependencies.

## [Ignored files and folders](#ignored-files-and-folders)

Vercel ignores certain files and folders by default and prevents them from being uploaded during the deployment process for security and performance reasons. Please note that these ignored files are only relevant when using Vercel CLI.

```
.hg
.git
.gitmodules
.svn
.cache
.next
.now
.vercel
.npmignore
.dockerignore
.gitignore
.*.swp
.DS_Store
.wafpicke-*
.lock-wscript
.env.local
.env.*.local
.venv
.yarn/cache
npm-debug.log
config.gypi
node_modules
__pycache__
venv
CVS
```

A complete list of files and folders ignored by Vercel during the Deployment process.

The `.vercel/output` directory is not ignored when [`vercel deploy --prebuilt`](/docs/cli/deploying-from-cli#deploying-from-local-build-prebuilt) is used to deploy a prebuilt Vercel Project, according to the [Build Output API](/docs/build-output-api/v3) specification.

You do not need to add any of the above files and folders to your `.vercelignore` file because it is done automatically by Vercel.

## [Special paths](#special-paths)

Vercel allows you to access the source code and build logs for your deployment using special pathnames for Build Logs and Source Protection. You can access this option from your project's Security settings.

All deployment URLs have two special pathnames to access the source code and the build logs:

*   `/_src`
*   `/_logs`

By default, these routes are protected so that they can only be accessed by you and the members of your Vercel Team.

![](/vc-ap-vercel-docs/_next/image?url=https%3A%2F%2Fassets.vercel.com%2Fimage%2Fupload%2Fv1689795055%2Fdocs-assets%2Fstatic%2Fdocs%2Fconcepts%2Fdeployments%2Fbuild-step%2Flogs-and-sources-light.png&w=3840&q=75)![](/vc-ap-vercel-docs/_next/image?url=https%3A%2F%2Fassets.vercel.com%2Fimage%2Fupload%2Fv1689795055%2Fdocs-assets%2Fstatic%2Fdocs%2Fconcepts%2Fdeployments%2Fbuild-step%2Flogs-and-sources-dark.png&w=3840&q=75)

Build Logs and Source Protection is enabled by default.

### [Source View](#source-view)

By appending `/_src` to a Deployment URL or [Custom Domain](/docs/domains/add-a-domain) in your web browser, you will be redirected to the Deployment inspector and be able to browse the sources and [build](/docs/deployments/configure-a-build) outputs.

### [Logs View](#logs-view)

By appending `/_logs` to a Deployment URL or [Custom Domain](/docs/domains/add-a-domain) in your web browser, you can see a real-time stream of logs from your deployment build processes by clicking on the Build Logs accordion.

### [Security considerations](#security-considerations)

The pathnames `/_src` and `/_logs` redirect to `https://vercel.com` and require logging into your Vercel account to access any sensitive information. By default, a third-party can never access your source or logs by crafting a deployment URL with one of these paths.

You can configure these paths to make them publicly accessible under the Security tab on the Project Settings page. You can learn more about making paths publicly accessible in the [Build Logs and Source Protection](/docs/projects/overview#logs-and-source-protection) section.

## [Git submodules](#git-submodules)

On Vercel, you can deploy [Git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) with a [Git provider](/docs/git) as long as the submodule is publicly accessible through the HTTP protocol. Git submodules that are private or requested over SSH will fail during the Build step. However, you can reference private repositories formatted as npm packages in your `package.json` file dependencies. Private repository modules require a special link syntax that varies according to the Git provider. For more information on this syntax, see "[How do I use private dependencies with Vercel?](/guides/using-private-dependencies-with-vercel)".

Last updated on June 26, 2025

# Build image overview

When you initiate a deployment, Vercel will [build your project](/docs/deployments/builds) within a container that has a predefined image. This build image is determined by the Node.js version selected in the [project settings](/docs/functions/runtimes/node-js#setting-the-node.js-version-in-project-settings).

| Node.js version | Build image | Base image | Deprecation date |  |
| --- | --- | --- | --- | --- |
| `22.x` `20.x` | [Build image](/docs/deployments/build-image/build-image) | [Amazon Linux 2023](https://aws.amazon.com/linux/amazon-linux-2023/) |  |  |
| `18.x` | [Build image (legacy)](/docs/builds/build-image/build-image#legacy-build-image) | [Amazon Linux 2](https://aws.amazon.com/amazon-linux-2/) | [August 1, 2025](/changelog/legacy-build-image-is-being-deprecated-on-august-1-2025-4rKrNPKXA3yiCV9c9h2Z5k) |  |

## [Runtime support](#runtime-support)

Vercel supports [multiple runtimes](https://vercel.com/docs/functions/runtimes), but different runtime versions are available depending on the selected build image. See the table below to learn about which runtime versions are supported by each image:

| Runtime | [Build image](/docs/deployments/build-image/build-image) | [Build image (legacy)](/docs/builds/build-image/build-image#legacy-build-image) |
| --- | --- | --- |
| [Node.js](/docs/functions/runtimes/node-js) | `22.x` `20.x` | `18.x` |
| [Edge](/docs/functions/runtimes/edge-runtime) |  |  |
| [Python](/docs/functions/runtimes/python) | `3.12` | `3.9` |
| [Ruby](/docs/functions/runtimes/ruby) | `3.3.x` | `3.2.x` |
| [Go RuntimeGo](/docs/functions/runtimes/go) |  |  |
| [Community Runtimes](/docs/functions/runtimes#community-runtimes) |  |  |

Last updated on April 10, 2025

# Build Queues on Vercel

When multiple deployments are started concurrently from code changes, Vercel's build system places deployments into one of the following queues:

*   [Concurrency queue](#concurrency-queue): The basics of build resource management.
*   [Git branch queue](#git-branch-queue): Understanding how builds to the same branch are managed.

## [Concurrency queue](#concurrency-queue)

This queue manages how many builds can run in parallel based on the number of [concurrent build slots](/docs/deployments/concurrent-builds) available to the team and user. If all concurrent build slots are in use, new builds are queued until a slot becomes available unless you have On-Demand Concurrent Builds [enabled at the project level](/docs/deployments/managing-builds#project-level-on-demand-concurrent-builds).

### [How concurrent build slots work](#how-concurrent-build-slots-work)

Concurrent build slots are the key factor in concurrent build queuing. They control how many builds can run at the same time and ensure efficient use of resources while prioritizing the latest changes.

Each account plan comes with a predefined number of build slots:

*   Hobby accounts allow one build at a time.
*   Pro accounts support up to 12 simultaneous builds.
*   Enterprise accounts can have [custom limits](/docs/deployments/concurrent-builds#usage-and-limits) based on their plan.

## [Git branch queue](#git-branch-queue)

When multiple builds are pushed to the same Git branch, they are handled sequentially. If new commits are pushed while a build is in progress:

1.  The current build is completed first.
2.  Queued builds for earlier commits are skipped.
3.  The most recent commit is built and deployed.

This ensures that only the latest changes are deployed, reducing unnecessary builds and improving deployment efficiency.

Enterprise users can use [Urgent On-Demand Concurrency](/docs/deployments/managing-builds#urgent-on-demand-concurrent-builds) to skip the Git branch queue for specific runs. However, this queue will still apply to project-level [On-Demand Concurrency](/docs/deployments/managing-builds#on-demand-concurrent-builds)

## [Concurrency on the same branch](#concurrency-on-the-same-branch)

It's possible for builds to be affected by both queues simultaneously. For example, if your builds are queued due to no slots being available and you submitted multiple commits to the same branch, the following will happen:

*   The latest commit to that branch will start building when a slot becomes available.
*   All previous commits to that branch will be skipped when that happens.

Last updated on March 21, 2025

# Configuring a Build

When you make a [deployment](/docs/deployments), Vercel builds your project. During this time, Vercel performs a "shallow clone" on your Git repository using the command `git clone --depth=10 (...)` and fetches ten levels of git commit history. This means that only the latest ten commits are pulled and not the entire repository history.

Vercel automatically configures the build settings for many front-end frameworks, but you can also customize the build according to your requirements.

To configure your Vercel build with customized settings, choose a project from the [dashboard](/dashboard) and go to its Settings tab.

The Build and Deployment section of the Settings tab offers the following options to customize your build settings:

*   [Framework Settings](#framework-settings)
*   [Root Directory](#root-directory)
*   [Node.js Version](/docs/functions/runtimes/node-js/node-js-versions#setting-the-node.js-version-in-project-settings)
*   [Prioritizing Production Builds](/docs/deployments/concurrent-builds#prioritize-production-builds)
*   [On-Demand Concurrent Builds](/docs/deployments/managing-builds#on-demand-concurrent-builds)

## [Framework Settings](#framework-settings)

If you'd like to override the settings or specify a different framework, you can do so from the Build & Development Settings section.

![](/vc-ap-vercel-docs/_next/image?url=https%3A%2F%2Fassets.vercel.com%2Fimage%2Fupload%2Fv1689795055%2Fdocs-assets%2Fstatic%2Fdocs%2Fconcepts%2Fdeployments%2Fbuild-step%2Fframework-settings-light.png&w=1920&q=75)![](/vc-ap-vercel-docs/_next/image?url=https%3A%2F%2Fassets.vercel.com%2Fimage%2Fupload%2Fv1689795055%2Fdocs-assets%2Fstatic%2Fdocs%2Fconcepts%2Fdeployments%2Fbuild-step%2Fframework-settings-dark.png&w=1920&q=75)

Framework settings.

### [Framework Preset](#framework-preset)

You have a wide range of frameworks to choose from, including, Next.js, Svelte, and Nuxt.js. In several use cases, Vercel automatically detects your project's framework and sets the best settings for you.

Inside the Framework Preset settings, use the drop-down menu to select the framework of your choice. This selection will be used for all deployments within your Project. The available frameworks are listed below:

Show More

However, if no framework is detected, "Other" will be selected. In this case, the Override toggle for the Build Command will be enabled by default so that you can enter the build command manually. The remaining deployment process is that for default frameworks.

If you would like to override Framework Preset for a specific deployment, add [`framework`](/docs/project-configuration#framework) to your `vercel.json` configuration.

### [Build Command](#build-command)

Vercel automatically configures the Build Command based on the framework. Depending on the framework, the Build Command can refer to the project’s `package.json` file.

For example, if [Next.js](https://nextjs.org) is your framework:

*   Vercel checks for the `build` command in `scripts` and uses this to build the project
*   If not, the `next build` will be triggered as the default Build Command

If you'd like to override the Build Command for all deployments in your Project, you can turn on the Override toggle and specify the custom command.

If you would like to override the Build Command for a specific deployment, add [`buildCommand`](/docs/project-configuration#buildcommand) to your `vercel.json` configuration.

If you update the **Override** setting, it will be applied on your next deployment.

### [Output Directory](#output-directory)

After building a project, most frameworks output the resulting build in a directory. Only the contents of this Output Directory will be served statically by Vercel.

If Vercel detects a framework, the output directory will automatically be configured.

If you update the **Override** setting, it will be applied on your next deployment.

For projects that [do not require building](#skip-build-step), you might want to serve the files in the root directory. In this case, do the following:

*   Choose "Other" as the Framework Preset. This sets the output directory as `public` if it exists or `.` (root directory of the project) otherwise
*   If your project doesn’t have a `public` directory, it will serve the files from the root directory
*   Alternatively, you can turn on the Override toggle and leave the field empty (in which case, the build step will be skipped)

If you would like to override the Output Directory for a specific deployment, add [`outputDirectory`](/docs/project-configuration#outputdirectory) to your `vercel.json` configuration.

### [Install Command](#install-command)

Vercel auto-detects the install command during the build step. It installs dependencies from `package.json`, including `devDependencies` ([which can be excluded](/docs/deployments/troubleshoot-a-build#excluding-development-dependencies)). The install path is set by the [root directory](#root-directory).

The install command can be managed in two ways: through a project override, or per-deployment. See [manually specifying a package manager](/docs/package-managers#manually-specifying-a-package-manager) for more details.

To learn what package managers are supported on Vercel, see the [package manager support](/docs/package-managers) documentation.

#### [Corepack](#corepack)

Corepack is considered [experimental](https://nodejs.org/docs/latest-v16.x/api/documentation.html#stability-index) and therefore, breaking changes or removal may occur in any future release of Node.js.

[Corepack](https://nodejs.org/docs/latest-v16.x/api/corepack.html) is an experimental tool that allows a Node.js project to pin a specific version of a package manager.

You can enable Corepack by adding an [environment variable](/docs/environment-variables) with name `ENABLE_EXPERIMENTAL_COREPACK` and value `1` to your Project.

Then, set the [`packageManager`](https://nodejs.org/docs/latest-v16.x/api/packages.html#packagemanager) property in the `package.json` file in the root of your repository. For example:

```
{
  "packageManager": "pnpm@7.5.1"
}
```

A `package.json` file with [pnpm](https://pnpm.io) version 7.5.1

#### [Custom Install Command for your API](#custom-install-command-for-your-api)

The Install Command defined in the Project Settings will be used for front-end frameworks that support Vercel functions for APIs.

If you're using [Vercel functions](/docs/functions) defined in the natively supported `api` directory, a different Install Command will be used depending on the language of the Vercel Function. You cannot customize this Install Command.

### [Development Command](#development-command)

This setting is relevant only if you’re using `vercel dev` locally to develop your project. Use `vercel dev` only if you need to use Vercel platform features like [Vercel functions](/docs/functions). Otherwise, it's recommended to use the development command your framework provides (such as `next dev` for Next.js).

The Development Command settings allow you to customize the behavior of `vercel dev`. If Vercel detects a framework, the development command will automatically be configured.

If you’d like to use a custom command for `vercel dev`, you can turn on the Override toggle. Please note the following:

*   If you specify a custom command, your command must pass your framework's `$PORT` variable (which contains the port number). For example, in [Next.js](https://nextjs.org/) you should use: `next dev --port $PORT`
*   If the development command is not specified, `vercel dev` will fail. If you've selected "Other" as the framework preset, the default development command will be empty
*   You must create a deployment and have your local project linked to the project on Vercel (using `vercel`). Otherwise, `vercel dev` will not work correctly

If you would like to override the Development Command, add [`devCommand`](/docs/project-configuration#devcommand) to your `vercel.json` configuration.

### [Skip Build Step](#skip-build-step)

Some static projects do not require building. For example, a website with only HTML/CSS/JS source files can be served as-is.

In such cases, you should:

*   Specify "Other" as the framework preset
*   Enable the Override option for the Build Command
*   Leave the Build Command empty

This prevents running the build, and your content is served directly.

## [Root Directory](#root-directory)

In some projects, the top-level directory of the repository may not be the root directory of the app you’d like to build. For example, your repository might have a front-end directory containing a stand-alone [Next.js](https://nextjs.org/) app.

For such cases, you can specify the project Root Directory. If you do so, please note the following:

*   Your app will not be able to access files outside of that directory. You also cannot use `..` to move up a level
*   This setting also applies to [Vercel CLI](/docs/cli). Instead of running `vercel <directory-name>` to deploy, specify `<directory-name>` here so you can just run `vercel`

If you update the root directory setting, it will be applied on your next deployment.

#### [Skipping unaffected projects](#skipping-unaffected-projects)

In a monorepo, you can [skip deployments](/docs/monorepos#skipping-unaffected-projects) for projects that were not affected by a commit. To configure:

1.  Navigate to the Build and Deployment page of your Project Settings
2.  Scroll down to Root Directory
3.  Enable the Skip deployment switch

Last updated on July 18, 2025


