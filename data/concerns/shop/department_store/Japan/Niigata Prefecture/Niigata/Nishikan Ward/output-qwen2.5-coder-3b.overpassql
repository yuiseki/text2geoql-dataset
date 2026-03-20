[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
area["name:en"="Niigata Prefecture"]->.inner;
(
  nwr["shop"~"department_store"](area.inner)(area.outer);
);
out geom;
