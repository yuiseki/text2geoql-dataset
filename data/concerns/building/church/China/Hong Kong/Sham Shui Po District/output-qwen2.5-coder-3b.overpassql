[out:json][timeout:30];
area["name:en"="Sham Shui Po District"]->.outer;
(
  nwr["building"~"church"](area.outer);
);
out geom;
