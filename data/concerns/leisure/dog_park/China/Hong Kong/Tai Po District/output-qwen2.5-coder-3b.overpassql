[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["leisure"~"dog_park"](area.outer);
);
out geom;
