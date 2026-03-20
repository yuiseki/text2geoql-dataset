[out:json][timeout:30];
area["name:en"="Totsuka Ward"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["shop"~"department_store"](area.inner)(area.outer);
);
out geom;
