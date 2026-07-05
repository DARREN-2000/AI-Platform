# FAQ

**Q: Is this a monorepo?**
A: No, the architecture strictly avoids monorepo assumptions. The five core repositories act as independent bounded contexts.

**Q: Can I use just one piece?**
A: Yes, each service is loosely coupled and can be run independently, provided you mock or supply the required API interfaces.
