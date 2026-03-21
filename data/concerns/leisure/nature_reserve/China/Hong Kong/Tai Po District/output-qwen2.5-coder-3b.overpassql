[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["leisure"~"nature_reserve"](area.outer);
);
out geom;
