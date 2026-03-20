[out:json][timeout:30];
area["name:ko"="노원구"]->.outer;
(
  nwr["amenity"="fast_food"]["cuisine"="burger"](area.outer);
);
out geom;
