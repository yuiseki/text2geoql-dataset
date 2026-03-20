[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
(
  nwr["tourism"="theme_park"](area.outer);
);
out geom;
