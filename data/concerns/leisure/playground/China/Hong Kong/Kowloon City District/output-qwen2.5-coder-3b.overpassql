[out:json][timeout:30];
area["name:en"="Kowloon City District"]->.outer;
(
  nwr["leisure"~"playground"](area.outer);
);
out geom;
