#  multistage file 
#  stage 1 - build the react app 
#  stage 2 - copy to nginx server

# ============= stage 1 ===================

FROM node:alpine AS build

WORKDIR /app/frontend

COPY package*.json .

RUN npm ci

COPY . .

RUN npm run build

# ============= stage 2 ===================

FROM nginx:alpine

COPY --from=build /app/frontend/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80 

CMD ["nginx", "-g", "daemon off;"]
