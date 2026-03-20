[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["building"~"church"](area.outer);
);
out geom;
