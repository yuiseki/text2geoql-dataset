[out:json][timeout:30];
area["name:en"="Yuen Long District"]->.outer;
(
  nwr["leisure"~"dog_park"](area.outer);
);
out geom;
