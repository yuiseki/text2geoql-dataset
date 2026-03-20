[out:json][timeout:30];
area["name:en"="Sai Kung District"]->.outer;
(
  nwr["shop"~"convenience"](area.outer);
);
out geom;
