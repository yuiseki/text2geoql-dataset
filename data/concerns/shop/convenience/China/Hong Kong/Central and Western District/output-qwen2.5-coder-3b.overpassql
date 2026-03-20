[out:json][timeout:30];
area["name:en"="Central and Western District"]->.outer;
(
  nwr["shop"~"convenience"](area.outer);
);
out geom;
