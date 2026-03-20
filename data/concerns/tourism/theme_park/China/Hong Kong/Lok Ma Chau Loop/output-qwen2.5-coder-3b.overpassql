[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["tourism"="theme_park"](area.outer);
);
out geom;
