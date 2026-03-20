[out:json][timeout:30];
area["name:en"="Pristina"]->.outer;
(
  nwr["building"~"church"](area.outer);
);
out geom;
