[out:json][timeout:30];
area["name:en"="Kowloon City District"]->.outer;
(
  nwr["leisure"~"dog_park"](area.outer);
);
out geom;
