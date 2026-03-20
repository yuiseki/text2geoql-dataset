[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["tourism"="hostel"](area.outer);
);
out geom;
