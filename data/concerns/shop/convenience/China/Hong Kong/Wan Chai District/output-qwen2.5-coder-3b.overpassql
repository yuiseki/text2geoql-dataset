[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["shop"~"convenience"](area.outer);
);
out geom;
