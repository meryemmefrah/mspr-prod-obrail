import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Configuration de Vite (outil de build et serveur de dev du frontend).
// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // écoute sur 0.0.0.0 (nécessaire dans un conteneur Docker)
    port: 5173,
  },
  preview: {
    host: true,
    port: 5173,
  },
});
