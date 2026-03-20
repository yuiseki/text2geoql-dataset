[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Guangdong Province"]->.inner;
(
  nwr["shop"~"department_store"](area.inner)(area.outer);
);
out geom;
