[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["shop"~"department_store"](area.outer);
);
out geom;
