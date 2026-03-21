[out:json][timeout:30];
area["name:en"="Longhua District"]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["leisure"~"playground"](area.inner)(area.outer);
);
out geom;
