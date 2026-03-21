[out:json][timeout:30];
area["name:en"="Tai Po District"]->.outer;
(
  nwr["office"~"government"](area.outer);
);
out geom;
