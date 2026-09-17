# Motos Leads Prioritization - Frontend

Base técnica de la interfaz web para la plataforma de priorización predictiva de leads en venta de motocicletas.

## Requisitos Previos

- **Node.js**: v18.0.0 o superior (recomendado LTS)
- **npm**: v9.0.0 o superior

## Instalación

1. Clonar el repositorio y posicionarse en la carpeta de frontend:
   ```bash
   cd Frontend
   ```

2. Configurar las variables de entorno:
   Copiar `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```
   Definir la URL base de FastAPI (por ejemplo `http://127.0.0.1:8000`):
   ```env
   FRONTEND_API_BASE_URL=http://127.0.0.1:8000
   ```

3. Instalar dependencias:
   ```bash
   npm install
   ```

## Scripts Disponibles

- `npm run dev`: Inicia el servidor de desarrollo local de Vite en `http://localhost:5173/`.
- `npm run build`: Valida tipos de TypeScript y compila el bundle optimizado para producción en `dist/`.
- `npm run typecheck`: Ejecuta la verificación estricta de tipos de TypeScript sin emitir archivos (`tsc -b --noEmit`).
- `npm run lint`: Analiza el código con `oxlint` para garantizar calidad y cumplimiento de reglas.
- `npm run preview`: Sirve localmente el bundle compilado de producción.

## Estructura del Proyecto

```text
Frontend/
├── .env.example            # Plantilla pública de variables de entorno (sin secretos)
├── .gitignore              # Exclusión de node_modules, build y archivos de entorno
├── index.html              # Punto de entrada HTML con metadatos descriptivos
├── package.json            # Dependencias y scripts de desarrollo
├── tsconfig.json           # Configuración base de TypeScript
├── tsconfig.app.json       # Configuración estricta de la aplicación cliente y alias @/*
├── vite.config.ts          # Configuración de Vite, Tailwind CSS y envPrefix FRONTEND_
└── src/
    ├── app/                # Enrutador (React Router), providers (TanStack Query) y App
    ├── components/         # Componentes compartidos
    │   ├── layout/         # RootLayout, Header adaptable y Sidebar responsive
    │   └── ui/             # Primitivas de UI (Button, Card, Badge, Loader, PlaceholderPage)
    ├── config/             # Configuración de entorno tipada (env.ts) y navegación (navigation.ts)
    ├── features/           # Módulos de dominio de negocio
    │   ├── leads/          # Tipos, servicios y hooks del módulo de leads
    │   ├── dashboard/      # Estructura inicial de métricas y KPIs
    │   ├── advisors/       # Estructura inicial de asesores comerciales
    │   └── catalog/        # Estructura inicial del catálogo de motocicletas
    ├── lib/                # Utilidades de estilos (cn) y formateadores
    ├── pages/              # Páginas conectadas al enrutador (placeholders tipados)
    │   ├── DashboardPage.tsx
    │   ├── LeadsPage.tsx
    │   ├── LeadDetailPage.tsx   # Ruta dinámica /leads/:leadId
    │   ├── AdvisorsPage.tsx
    │   ├── CatalogPage.tsx
    │   └── NotFoundPage.tsx     # Manejador de ruta 404
    ├── services/           # Capa de servicios e integración HTTP
    │   └── apiClient.ts    # Cliente HTTP genérico sin endpoints de negocio inventados
    ├── index.css           # Configuración global de estilos con Tailwind CSS
    └── main.tsx            # Punto de entrada de React con StrictMode
```

## Rutas Configuradas

- `/dashboard`: Panel general de métricas comerciales.
- `/leads`: Listado priorizado de prospectos comerciales.
- `/leads/:leadId`: Ficha y diagnóstico detallado de un lead específico.
- `/advisors`: Equipo y capacidad de asesores comerciales.
- `/catalog`: Catálogo de modelos de motocicletas y stock.
- `*`: Página 404 para rutas no encontradas.
