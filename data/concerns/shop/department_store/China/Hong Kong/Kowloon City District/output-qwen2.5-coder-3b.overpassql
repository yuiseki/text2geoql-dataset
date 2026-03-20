[out:json][timeout:30];
area["name:en"="Kowloon City District"]->.outer;
(
  nwr["shop"~"department_store"](area.outer);
);
out geom;
