[out:json][timeout:30];
area["name:en"="Kwun Tong District"]->.outer;
(
  nwr["leisure"~"dog_park"](area.outer);
);
out geom;
