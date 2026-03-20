[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
(
  nwr["tourism"="theme_park"](area.outer);
);
out geom;
