# Contributing to Experimentor

We welcome contributions from anyone. We aim at being an open and inclusive community. Programmers of different experience levels and backgrounds can contribute to different parts of the program. Please, check the following guidelines to get started as quickly and smoothly as possible. 

**Be respectful**

We won't tolerate any comments that don't follow the common sense of tolerance between peers, regardless of your background, programming proficiency, or academic status. We are an inclusive community, and we want to encourage people from all backgrounds to be able to contribute code. 

Any remarks, comments, or public opinions, expressed in this repository or in any other medium will result in an immediate ban from the project. If you ever feel uncomfortable because of someone's behavior, please reach out to: hey@aquiles.me

## Start by Forking
To get started, create a **fork** of this repository. This will duplicate the code into your own space. You will be free to update, change, test, play around, and do version control independently from the main code. 

## Rebase to Develop
Once you are happy with the changes you have done to the code, **rebase** to the latest version available on the **development branch**. This will ensure that your changes are not breaking anything important. 

## Squash before making a pull request
Probably you have worked for a while on a new feature, improved documentation, etc. The best is to squash all the commits into a single one, so they are easier to review, and it makes a much clearer history of the main project. This will help us to keep an up-to-date changelog. 

### Better Atomic Commits
Be sure that the pull requests you submit are relative to specific changes. For example, if you create a new driver AND solve a bug in the base code, create two different pull requests addressing these changes separately. This will make the code review process much smoother, because different people can take care of different things. 

## Tests
If you are adding code, be sure to update the respective tests, or add new tests. The overall idea is that every pull request should have at least the same coverage than the base commit, but never less. The **exception** are drivers, which are harder to test without access to hardware. We are still working on the best approach to testing drivers. 

## Ideas for Beginners
If you are a beginner to the project, to Python, or to programming in general, the best way of starting is by improving the documentation. Most likely, you started by reading the guides and you found something you didn't like, or that you think it could be better. Just go ahead to improving it and submitting your first pull request. 

Another great way of getting started is by creating examples. If you used Experimentor for something that can be interesting for the community, you can submit a a new example so we can all learn from what you have done. If you submit an example, include good documentation to guide the rest through your thinking process. 


