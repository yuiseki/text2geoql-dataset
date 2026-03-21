[out:json][timeout:30];
area["name:en"="Sai Kung District"]->.outer;
(
  nwr["leisure"~"dog_park"](area.outer);
);
out geom;
