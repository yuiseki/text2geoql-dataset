[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
(
  nwr["tourism"="theme_park"](area.outer);
);
out geom;
