[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["leisure"~"dog_park"](area.outer);
);
out geom;
