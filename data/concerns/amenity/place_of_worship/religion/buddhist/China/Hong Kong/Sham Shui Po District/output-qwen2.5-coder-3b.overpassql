[out:json][timeout:30];
area["name:en"="Sham Shui Po District"]->.outer;
(
  nwr["building"~"temple"](area.outer);
);
out geom;
