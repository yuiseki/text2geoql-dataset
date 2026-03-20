[out:json][timeout:30];
area["name:en"="Kwai Tsing District"]->.outer;
(
  nwr["shop"~"convenience"](area.outer);
);
out geom;
