[out:json][timeout:30];
area["name:en"="Futian District"]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["shop"~"department_store"](area.inner)(area.outer);
);
out geom;
