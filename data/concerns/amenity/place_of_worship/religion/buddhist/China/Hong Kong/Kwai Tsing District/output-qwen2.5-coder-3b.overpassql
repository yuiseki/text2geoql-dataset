[out:json][timeout:30];
area["name:en"="Kwai Tsing District"]->.outer;
(
  nwr["building"~"temple"](area.outer);
);
out geom;
