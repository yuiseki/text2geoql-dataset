[out:json][timeout:30];
area["name:en"="Yau Tsim Mong District"]->.outer;
(
  nwr["shop"~"department_store"](area.outer);
);
out geom;
