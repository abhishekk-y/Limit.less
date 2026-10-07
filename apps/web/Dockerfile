FROM node:22-alpine AS build
WORKDIR /app
COPY apps/web/package*.json ./
RUN npm ci
COPY apps/web ./
ENV NEXT_TELEMETRY_DISABLED=1
ARG API_INTERNAL_URL=http://api:8000
ENV API_INTERNAL_URL=$API_INTERNAL_URL
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1
COPY --from=build /app ./
USER node
EXPOSE 3000
CMD ["npm", "start", "--", "--hostname", "0.0.0.0"]
