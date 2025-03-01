import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
// Uncomment for OAuth login
// import GoogleProvider from "next-auth/providers/google";

export default NextAuth({
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        // Replace this with a real user authentication logic
        const user = { id: "1", name: "Test User", email: credentials.email };

        if (credentials.password === "password123") {
          return user;
        }
        throw new Error("Invalid credentials");
      }
    }),
    // Uncomment this if using Google authentication
    // GoogleProvider({
    //   clientId: process.env.GOOGLE_CLIENT_ID,
    //   clientSecret: process.env.GOOGLE_CLIENT_SECRET
    // })
  ],
  pages: {
    signIn: "/login",  // Custom login page
  },
  session: {
    strategy: "jwt"
  }
});
