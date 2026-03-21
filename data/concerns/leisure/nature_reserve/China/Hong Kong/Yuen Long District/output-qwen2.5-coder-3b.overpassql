[out:json][timeout:30];
area["name:en"="Yuen Long District"]->.outer;
(
  nwr["leisure"~"nature_reserve"](area.outer);
);
out geom;
