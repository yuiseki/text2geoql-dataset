[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
(
  nwr["tourism"="theme_park"](area.outer);
);
out geom;
